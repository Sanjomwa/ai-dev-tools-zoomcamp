"""Persisted test suite for the chores app.

Covers the six pieces of behaviour the homework grades on:

* ``Member.save()`` auto-numbering (rotation order),
* ``mark_done``'s holder advance,
* the ``require_identity`` session guard,
* ``Chore.is_overdue`` (rolling-window overdue calc),
* the identity-pick view,
* the chore list view, plus one end-to-end wiring check.

Plain ``TestCase`` + ``unittest.mock`` only -- no factory_boy / pytest-django /
freezegun.
"""

from datetime import datetime, timedelta, timezone as dt_timezone
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Chore, Household, Member


def backdate(chore, when):
    """Set ``created_at`` (``auto_now_add``, so unsettable via ``save()``).

    The ``refresh_from_db()`` is load-bearing, not hygiene: ``Chore.save()``
    writes every column from the in-memory instance, so a later ``save()`` on a
    chore whose ``created_at`` attribute is still the original value would
    silently undo the backdate.
    """
    Chore.objects.filter(pk=chore.pk).update(created_at=when)
    chore.refresh_from_db()


class AuthClientMixin:
    """Session-cookie identity: 'authenticated' just means ``member_id`` is set."""

    def login_as(self, member):
        session = self.client.session
        session["member_id"] = member.id
        session.save()


class MemberOrderingTests(TestCase):
    """The ``Member.save()`` override that assigns ``order``."""

    def test_first_member_gets_order_zero(self):
        h = Household.objects.create(name="H")
        first = Member.objects.create(household=h, name="A")
        self.assertEqual(first.order, 0)

    def test_sequential_members_increment(self):
        h = Household.objects.create(name="H")
        a = Member.objects.create(household=h, name="A")
        b = Member.objects.create(household=h, name="B")
        c = Member.objects.create(household=h, name="C")
        self.assertEqual([a.order, b.order, c.order], [0, 1, 2])

    def test_order_is_scoped_per_household(self):
        h1 = Household.objects.create(name="One")
        h2 = Household.objects.create(name="Two")
        Member.objects.create(household=h1, name="A")
        Member.objects.create(household=h1, name="B")
        # h2's first member restarts at 0 -- it does not continue h1's count.
        h2_first = Member.objects.create(household=h2, name="C")
        self.assertEqual(h2_first.order, 0)

    def test_resaving_a_member_does_not_renumber_it(self):
        # Highest-value case: catches a "recompute order on every save" bug.
        # Resave the NON-max member -- a recompute would push it to max+1 (2),
        # whereas resaving the max member could coincidentally return its value.
        h = Household.objects.create(name="H")
        a = Member.objects.create(household=h, name="A")  # order 0
        Member.objects.create(household=h, name="B")      # order 1
        a.name = "Renamed"
        a.save()
        a.refresh_from_db()
        self.assertEqual(a.order, 0)

    def test_deleting_a_middle_member_leaves_a_gap(self):
        h = Household.objects.create(name="H")
        Member.objects.create(household=h, name="A")       # 0
        b = Member.objects.create(household=h, name="B")   # 1
        Member.objects.create(household=h, name="C")       # 2
        b.delete()
        # New member continues from the current max, it does not backfill the 1.
        d = Member.objects.create(household=h, name="D")
        self.assertEqual(d.order, 3)
        self.assertEqual(list(h.members.values_list("order", flat=True)), [0, 2, 3])


class RotationTests(AuthClientMixin, TestCase):
    """``mark_done``'s holder advance -- always via an authenticated session."""

    def make_household(self, n_members=2):
        h = Household.objects.create(name="H")
        members = [Member.objects.create(household=h, name=f"M{i}") for i in range(n_members)]
        return h, members

    def make_chore(self, household, holder, name="Chore", cadence=Chore.Cadence.DAILY):
        return Chore.objects.create(
            household=household, name=name, cadence=cadence, current_holder=holder
        )

    def test_rotates_to_next_member_and_persists_and_redirects(self):
        h, (m0, m1) = self.make_household(2)
        chore = self.make_chore(h, m0)
        self.login_as(m0)
        resp = self.client.post(reverse("mark_done", args=[chore.id]))
        self.assertRedirects(resp, reverse("chore_list"))
        chore.refresh_from_db()  # check the DB, not the in-memory object
        self.assertEqual(chore.current_holder, m1)

    def test_wraps_from_last_member_back_to_first(self):
        h, (m0, m1) = self.make_household(2)
        chore = self.make_chore(h, m1)  # holder is the last in order
        self.login_as(m1)
        self.client.post(reverse("mark_done", args=[chore.id]))
        chore.refresh_from_db()
        self.assertEqual(chore.current_holder, m0)

    def test_skips_gaps_in_order(self):
        h = Household.objects.create(name="H")
        m0 = Member.objects.create(household=h, name="A")             # order 0
        m2 = Member.objects.create(household=h, name="B", order=2)
        Member.objects.create(household=h, name="C", order=5)
        chore = self.make_chore(h, m0)
        self.login_as(m0)
        self.client.post(reverse("mark_done", args=[chore.id]))
        chore.refresh_from_db()
        # Advances to the next member by position, i.e. order 2 -- not a
        # nonexistent order-1 row.
        self.assertEqual(chore.current_holder, m2)

    def test_single_member_household_wraps_to_itself(self):
        h, (m0,) = self.make_household(1)
        chore = self.make_chore(h, m0)
        self.login_as(m0)
        resp = self.client.post(reverse("mark_done", args=[chore.id]))
        self.assertRedirects(resp, reverse("chore_list"))
        chore.refresh_from_db()
        self.assertEqual(chore.current_holder, m0)
        self.assertIsNotNone(chore.last_completed_at)

    def test_last_completed_at_goes_from_null_to_set_and_updates_again(self):
        h, (m0, m1) = self.make_household(2)
        chore = self.make_chore(h, m0)
        self.assertIsNone(chore.last_completed_at)
        self.login_as(m0)

        self.client.post(reverse("mark_done", args=[chore.id]))
        chore.refresh_from_db()
        first = chore.last_completed_at
        self.assertIsNotNone(first)

        # The first completion rotated the holder to m1 (issue #8: only the
        # current holder may mark done), so complete the second one as m1.
        self.login_as(m1)
        self.client.post(reverse("mark_done", args=[chore.id]))
        chore.refresh_from_db()
        self.assertGreater(chore.last_completed_at, first)

    def test_does_not_affect_a_sibling_chore(self):
        h, (m0, m1) = self.make_household(2)
        target = self.make_chore(h, m0, name="Target")
        sibling = self.make_chore(h, m0, name="Sibling")
        self.login_as(m0)
        self.client.post(reverse("mark_done", args=[target.id]))
        sibling.refresh_from_db()
        self.assertEqual(sibling.current_holder, m0)

    def test_rotation_only_considers_the_chores_own_household(self):
        h1 = Household.objects.create(name="One")
        a0 = Member.objects.create(household=h1, name="A0")
        a1 = Member.objects.create(household=h1, name="A1")
        h2 = Household.objects.create(name="Two")
        Member.objects.create(household=h2, name="B0")
        Member.objects.create(household=h2, name="B1")
        chore = self.make_chore(h1, a0)
        self.login_as(a0)
        self.client.post(reverse("mark_done", args=[chore.id]))
        chore.refresh_from_db()
        self.assertEqual(chore.current_holder, a1)
        self.assertIn(chore.current_holder, [a0, a1])

    def test_get_while_authenticated_is_rejected_405(self):
        h, (m0, m1) = self.make_household(2)
        chore = self.make_chore(h, m0)
        self.login_as(m0)
        resp = self.client.get(reverse("mark_done", args=[chore.id]))
        self.assertEqual(resp.status_code, 405)

    def test_mark_done_clears_an_overdue_flag(self):
        h, (m0, m1) = self.make_household(2)
        chore = self.make_chore(h, m0)
        backdate(chore, timezone.now() - timedelta(hours=25))
        self.assertTrue(chore.is_overdue)
        self.login_as(m0)
        self.client.post(reverse("mark_done", args=[chore.id]))
        chore.refresh_from_db()
        self.assertFalse(chore.is_overdue)


class MarkDoneHolderRestrictionTests(AuthClientMixin, TestCase):
    """``mark_done`` may only be triggered by the chore's current holder (issue #8)."""

    def setUp(self):
        self.h = Household.objects.create(name="H")
        self.holder = Member.objects.create(household=self.h, name="Holder")
        self.other = Member.objects.create(household=self.h, name="Other")
        self.chore = Chore.objects.create(
            household=self.h,
            name="Dishes",
            cadence=Chore.Cadence.DAILY,
            current_holder=self.holder,
        )

    def test_non_holder_post_is_forbidden_and_has_no_side_effect(self):
        self.login_as(self.other)
        resp = self.client.post(reverse("mark_done", args=[self.chore.id]))
        self.assertEqual(resp.status_code, 403)
        self.chore.refresh_from_db()
        self.assertEqual(self.chore.current_holder, self.holder)
        self.assertIsNone(self.chore.last_completed_at)

    def test_holder_post_still_rotates_and_stamps(self):
        self.login_as(self.holder)
        resp = self.client.post(reverse("mark_done", args=[self.chore.id]))
        self.assertRedirects(resp, reverse("chore_list"))
        self.chore.refresh_from_db()
        self.assertEqual(self.chore.current_holder, self.other)
        self.assertIsNotNone(self.chore.last_completed_at)


class RequireIdentityGuardTests(AuthClientMixin, TestCase):
    """``chores/guards.py`` -- the session-identity redirect."""

    def setUp(self):
        self.h = Household.objects.create(name="H")
        self.holder = Member.objects.create(household=self.h, name="Holder")
        self.other = Member.objects.create(household=self.h, name="Other")
        self.chore = Chore.objects.create(
            household=self.h,
            name="Dishes",
            cadence=Chore.Cadence.DAILY,
            current_holder=self.holder,
        )

    def test_chore_list_redirects_with_no_session(self):
        resp = self.client.get(reverse("chore_list"))
        self.assertRedirects(resp, reverse("identity_pick"))

    def test_chore_list_allows_a_valid_session(self):
        self.login_as(self.holder)
        resp = self.client.get(reverse("chore_list"))
        self.assertEqual(resp.status_code, 200)

    def test_chore_list_redirects_on_a_stale_deleted_member(self):
        # A deleted NON-holder: PROTECT blocks deleting an actual holder.
        self.login_as(self.other)
        self.other.delete()
        resp = self.client.get(reverse("chore_list"))
        self.assertRedirects(resp, reverse("identity_pick"))

    def test_chore_list_redirects_on_a_member_id_that_never_existed(self):
        session = self.client.session
        session["member_id"] = 999999
        session.save()
        resp = self.client.get(reverse("chore_list"))
        self.assertRedirects(resp, reverse("identity_pick"))

    def test_identity_pick_is_never_guarded(self):
        # Arguably the most important test here: a regression makes this an
        # infinite redirect loop.
        resp = self.client.get(reverse("identity_pick"))
        self.assertEqual(resp.status_code, 200)

        session = self.client.session
        session["member_id"] = 999999  # stale
        session.save()
        resp = self.client.get(reverse("identity_pick"))
        self.assertEqual(resp.status_code, 200)

    def test_unauthenticated_get_to_mark_done_redirects_not_405(self):
        # Pins decorator order: the identity check runs before the POST check.
        resp = self.client.get(reverse("mark_done", args=[self.chore.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("identity_pick"))

    def test_unauthenticated_post_to_mark_done_has_no_side_effect(self):
        resp = self.client.post(reverse("mark_done", args=[self.chore.id]))
        self.assertRedirects(resp, reverse("identity_pick"))
        self.chore.refresh_from_db()
        self.assertEqual(self.chore.current_holder, self.holder)
        self.assertIsNone(self.chore.last_completed_at)


class OverdueTests(TestCase):
    """``Chore.is_overdue`` -- pure model tests, no client."""

    def setUp(self):
        self.h = Household.objects.create(name="H")
        self.m = Member.objects.create(household=self.h, name="M")

    def make_chore(self, cadence=Chore.Cadence.DAILY, last_completed_at=None):
        return Chore.objects.create(
            household=self.h,
            name="Chore",
            cadence=cadence,
            current_holder=self.m,
            last_completed_at=last_completed_at,
        )

    def test_daily_overdue_depends_on_elapsed_time(self):
        chore = self.make_chore(last_completed_at=timezone.now() - timedelta(hours=23))
        self.assertFalse(chore.is_overdue)
        chore.last_completed_at = timezone.now() - timedelta(hours=25)
        self.assertTrue(chore.is_overdue)

    def test_boundary_is_strictly_greater_than(self):
        chore = self.make_chore()
        chore.last_completed_at = timezone.now() - timedelta(hours=24) + timedelta(seconds=1)
        self.assertFalse(chore.is_overdue)  # just inside the window
        chore.last_completed_at = timezone.now() - timedelta(hours=24) - timedelta(seconds=1)
        self.assertTrue(chore.is_overdue)   # just outside

    def test_overdue_is_rolling_time_not_calendar_day(self):
        # Pin "now" just after midnight. A 1-hour gap that crosses the
        # calendar-day boundary must NOT be overdue; a 25-hour gap must be.
        chore = self.make_chore(cadence=Chore.Cadence.DAILY)
        fixed_now = datetime(2026, 1, 2, 0, 30, tzinfo=dt_timezone.utc)
        with patch("chores.models.timezone.now", return_value=fixed_now):
            chore.last_completed_at = datetime(2026, 1, 1, 23, 30, tzinfo=dt_timezone.utc)
            self.assertFalse(chore.is_overdue)
            chore.last_completed_at = datetime(2025, 12, 31, 23, 30, tzinfo=dt_timezone.utc)
            self.assertTrue(chore.is_overdue)

    def test_never_completed_falls_back_to_created_at(self):
        chore = self.make_chore()  # last_completed_at is None
        backdate(chore, timezone.now() - timedelta(hours=25))
        self.assertIsNone(chore.last_completed_at)
        self.assertTrue(chore.is_overdue)

    def test_last_completed_at_takes_precedence_over_created_at(self):
        chore = self.make_chore()
        backdate(chore, timezone.now() - timedelta(days=100))
        chore.last_completed_at = timezone.now() - timedelta(hours=1)
        chore.save()
        chore.refresh_from_db()
        self.assertFalse(chore.is_overdue)

    def test_weekly_cadence_uses_the_weekly_window(self):
        chore = self.make_chore(cadence=Chore.Cadence.WEEKLY)
        # 6 days would be overdue for a daily chore -- proves the cadence is wired.
        chore.last_completed_at = timezone.now() - timedelta(days=6)
        self.assertFalse(chore.is_overdue)
        chore.last_completed_at = timezone.now() - timedelta(days=8)
        self.assertTrue(chore.is_overdue)

    def test_monthly_cadence_uses_the_monthly_window(self):
        chore = self.make_chore(cadence=Chore.Cadence.MONTHLY)
        # 20 days would be overdue for a weekly chore.
        chore.last_completed_at = timezone.now() - timedelta(days=20)
        self.assertFalse(chore.is_overdue)
        chore.last_completed_at = timezone.now() - timedelta(days=31)
        self.assertTrue(chore.is_overdue)


class IdentityPickTests(TestCase):
    """The identity-pick view (issue #3)."""

    def test_lists_all_members(self):
        h = Household.objects.create(name="H")
        Member.objects.create(household=h, name="Alice")
        Member.objects.create(household=h, name="Bob")
        Member.objects.create(household=h, name="Carol")
        resp = self.client.get(reverse("identity_pick"))
        for name in ("Alice", "Bob", "Carol"):
            self.assertContains(resp, name)

    def test_members_appear_in_meta_order_not_insertion_order(self):
        h = Household.objects.create(name="H")
        Member.objects.create(household=h, name="Alice")            # order 0, inserted 1st
        Member.objects.create(household=h, name="Carol", order=5)   # inserted 2nd
        Member.objects.create(household=h, name="Bob", order=2)     # inserted 3rd
        body = self.client.get(reverse("identity_pick")).content.decode()
        # Meta ordering is ["order"], so despite the insertion order (which would
        # give Alice, Carol, Bob) the page must read Alice, Bob, Carol.
        self.assertLess(body.index("Alice"), body.index("Bob"))
        self.assertLess(body.index("Bob"), body.index("Carol"))

    def test_zero_household_shows_a_plain_message(self):
        resp = self.client.get(reverse("identity_pick"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No household")

    def test_zero_member_household_shows_a_plain_message(self):
        Household.objects.create(name="Empty")
        resp = self.client.get(reverse("identity_pick"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "no members")

    def test_picking_sets_the_session_and_redirects_to_chore_list(self):
        h = Household.objects.create(name="H")
        alice = Member.objects.create(household=h, name="Alice")
        resp = self.client.get(reverse("pick_identity", args=[alice.id]))
        self.assertRedirects(resp, reverse("chore_list"), fetch_redirect_response=False)
        self.assertEqual(self.client.session["member_id"], alice.id)

    def test_picking_again_overwrites_the_existing_identity(self):
        h = Household.objects.create(name="H")
        alice = Member.objects.create(household=h, name="Alice")
        bob = Member.objects.create(household=h, name="Bob")
        self.client.get(reverse("pick_identity", args=[alice.id]))
        self.assertEqual(self.client.session["member_id"], alice.id)
        self.client.get(reverse("pick_identity", args=[bob.id]))
        self.assertEqual(self.client.session["member_id"], bob.id)


class SwitchIdentityTests(AuthClientMixin, TestCase):
    """The switch-identity link/view (issue #11)."""

    def setUp(self):
        self.h = Household.objects.create(name="H")
        self.alice = Member.objects.create(household=self.h, name="Alice")
        self.bob = Member.objects.create(household=self.h, name="Bob")

    def test_switch_clears_the_session_and_redirects_to_identity_pick(self):
        self.login_as(self.alice)
        resp = self.client.get(reverse("switch_identity"))
        self.assertRedirects(resp, reverse("identity_pick"))
        self.assertNotIn("member_id", self.client.session)

    def test_chore_list_offers_the_switch_link(self):
        self.login_as(self.alice)
        resp = self.client.get(reverse("chore_list"))
        self.assertContains(resp, reverse("switch_identity"))

    def test_chores_page_redirects_to_identity_pick_after_switching(self):
        # AC #2: a fresh request to /chores/ must fall back through the
        # require_identity guard once the identity has been cleared.
        self.login_as(self.alice)
        self.client.get(reverse("switch_identity"))
        resp = self.client.get(reverse("chore_list"))
        self.assertRedirects(resp, reverse("identity_pick"))

    def test_switching_without_an_identity_is_a_harmless_no_op(self):
        resp = self.client.get(reverse("switch_identity"))
        self.assertRedirects(resp, reverse("identity_pick"))
        self.assertNotIn("member_id", self.client.session)

    def test_after_switching_a_new_identity_can_be_picked(self):
        self.login_as(self.alice)
        self.client.get(reverse("switch_identity"))
        self.client.get(reverse("pick_identity", args=[self.bob.id]))
        self.assertEqual(self.client.session["member_id"], self.bob.id)


class ChoreListTests(AuthClientMixin, TestCase):
    """The chore list view (authenticated)."""

    def setUp(self):
        self.h = Household.objects.create(name="H")
        self.holder = Member.objects.create(household=self.h, name="Robin")
        self.login_as(self.holder)

    def test_shows_name_holder_and_human_readable_cadence_label(self):
        Chore.objects.create(
            household=self.h,
            name="Take out trash",
            cadence=Chore.Cadence.WEEKLY,
            current_holder=self.holder,
        )
        resp = self.client.get(reverse("chore_list"))
        self.assertContains(resp, "Take out trash")
        self.assertContains(resp, "Robin")
        self.assertContains(resp, "Weekly")  # not the raw "weekly"

    def test_zero_chores_shows_a_plain_message(self):
        resp = self.client.get(reverse("chore_list"))
        self.assertContains(resp, "No chores yet")

    def test_overdue_flag_appears_and_is_tied_to_the_right_chore(self):
        overdue = Chore.objects.create(
            household=self.h, name="Dishes", cadence=Chore.Cadence.DAILY, current_holder=self.holder
        )
        backdate(overdue, timezone.now() - timedelta(hours=25))
        Chore.objects.create(
            household=self.h, name="Vacuum", cadence=Chore.Cadence.DAILY, current_holder=self.holder
        )
        resp = self.client.get(reverse("chore_list"))
        # One flag rendered...
        self.assertContains(resp, "Overdue", count=1)
        # ...on the right chore. Use the context, not markup order: Chore has no
        # Meta.ordering so row order is not guaranteed.
        by_name = {c.name: c for c in resp.context["chores"]}
        self.assertTrue(by_name["Dishes"].is_overdue)
        self.assertFalse(by_name["Vacuum"].is_overdue)


class EndToEndFlowTests(TestCase):
    """One real redirect-following pass, plus the holder-delete invariant."""

    def test_full_happy_path(self):
        h = Household.objects.create(name="H")
        alex = Member.objects.create(household=h, name="Alex")
        blair = Member.objects.create(household=h, name="Blair")
        chore = Chore.objects.create(
            household=h, name="Sweep floors", cadence=Chore.Cadence.DAILY, current_holder=alex
        )

        # Unauthenticated GET / -> identity pick, listing members.
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Alex")

        # Pick a member -> chore list loads with the chore.
        resp = self.client.get(reverse("pick_identity", args=[alex.id]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Sweep floors")
        self.assertContains(resp, "Alex")

        # POST mark-done -> redirects back, next holder now shown.
        resp = self.client.post(reverse("mark_done", args=[chore.id]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Blair")
        chore.refresh_from_db()
        self.assertEqual(chore.current_holder, blair)

    def test_current_holder_cannot_be_deleted(self):
        # Documents the invariant that keeps the guard's stale-id case narrow.
        h = Household.objects.create(name="H")
        m = Member.objects.create(household=h, name="M")
        Chore.objects.create(
            household=h, name="Chore", cadence=Chore.Cadence.DAILY, current_holder=m
        )
        with self.assertRaises(ProtectedError):
            m.delete()


class SeedDemoCommandTests(AuthClientMixin, TestCase):
    """``manage.py seed_demo`` -- the dev/QA data seeder (issue #13)."""

    def run_seed(self):
        out = StringIO()
        call_command("seed_demo", stdout=out)
        return out.getvalue()

    def test_seeds_a_household_with_members_and_varied_chores(self):
        self.run_seed()

        self.assertEqual(Household.objects.count(), 1)
        household = Household.objects.get()
        self.assertGreaterEqual(household.members.count(), 3)
        chores = household.chores.all()
        self.assertGreaterEqual(chores.count(), 3)
        # "varied cadences" -- more than one distinct cadence is present.
        self.assertGreater(len({c.cadence for c in chores}), 1)
        # Every holder belongs to this household, so mark_done can't 500.
        member_ids = set(household.members.values_list("pk", flat=True))
        self.assertTrue(all(c.current_holder_id in member_ids for c in chores))

    def test_seeded_data_is_visible_in_the_app_views(self):
        self.run_seed()
        household = Household.objects.get()

        # Identity-pick lists the seeded members.
        resp = self.client.get(reverse("identity_pick"))
        for member in household.members.all():
            self.assertContains(resp, member.name)

        # Pick one, then the chore list shows the seeded chores and an overdue flag.
        first = household.members.first()
        self.client.get(reverse("pick_identity", args=[first.id]))
        resp = self.client.get(reverse("chore_list"))
        self.assertEqual(resp.status_code, 200)
        for chore in household.chores.all():
            self.assertContains(resp, chore.name)
        self.assertContains(resp, "Overdue")

    def test_running_twice_is_a_safe_no_op(self):
        self.run_seed()
        h_count, m_count, c_count = (
            Household.objects.count(),
            Member.objects.count(),
            Chore.objects.count(),
        )
        # Rotate a chore through the real mark-done view so its state genuinely
        # differs from what the seed's `defaults` would write, then re-run: the
        # second run must not renumber, re-add, or reset anything.
        chore = Chore.objects.first()
        self.login_as(chore.current_holder)
        self.client.post(reverse("mark_done", args=[chore.id]))
        chore.refresh_from_db()
        rotated_holder, stamp = chore.current_holder, chore.last_completed_at

        self.run_seed()

        self.assertEqual(Household.objects.count(), h_count)
        self.assertEqual(Member.objects.count(), m_count)
        self.assertEqual(Chore.objects.count(), c_count)
        chore.refresh_from_db()
        self.assertEqual(chore.current_holder, rotated_holder)
        self.assertEqual(chore.last_completed_at, stamp)


class HouseholdManageTests(TestCase):
    """The in-app household/member management UI (issue #9)."""

    def test_page_is_not_gated_by_require_identity(self):
        # No session, no members -- the page must still render so a brand-new
        # household can be populated from zero.
        Household.objects.create(name="H")
        resp = self.client.get(reverse("household_manage"))
        self.assertEqual(resp.status_code, 200)

    def test_page_shows_household_name_and_members_in_rotation_order(self):
        h = Household.objects.create(name="The Nest")
        Member.objects.create(household=h, name="Alice")            # order 0, inserted 1st
        Member.objects.create(household=h, name="Carol", order=5)   # inserted 2nd
        Member.objects.create(household=h, name="Bob", order=2)     # inserted 3rd
        body = self.client.get(reverse("household_manage")).content.decode()
        self.assertIn("The Nest", body)
        # Meta ordering is ["order"], so the page must read Alice, Bob, Carol
        # despite the insertion order.
        self.assertLess(body.index("Alice"), body.index("Bob"))
        self.assertLess(body.index("Bob"), body.index("Carol"))

    def test_add_member_appends_to_end_of_rotation_via_auto_order(self):
        h = Household.objects.create(name="H")
        Member.objects.create(household=h, name="A")  # order 0
        Member.objects.create(household=h, name="B")  # order 1
        resp = self.client.post(reverse("add_member"), {"name": "C"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        added = Member.objects.get(name="C")
        self.assertEqual(added.household, h)
        self.assertEqual(added.order, 2)
        self.assertEqual(
            list(h.members.values_list("name", flat=True)), ["A", "B", "C"]
        )

    def test_add_member_rejects_a_blank_name(self):
        h = Household.objects.create(name="H")
        resp = self.client.post(reverse("add_member"), {"name": "   "}, follow=True)
        self.assertEqual(h.members.count(), 0)
        self.assertContains(resp, "blank")

    def test_rename_member_is_reflected_in_chore_list_and_identity_pick(self):
        h = Household.objects.create(name="H")
        m = Member.objects.create(household=h, name="OldName")
        Chore.objects.create(
            household=h, name="Dishes", cadence=Chore.Cadence.DAILY, current_holder=m
        )
        self.client.post(reverse("rename_member", args=[m.id]), {"name": "NewName"})
        m.refresh_from_db()
        self.assertEqual(m.name, "NewName")

        session = self.client.session
        session["member_id"] = m.id
        session.save()
        self.assertContains(self.client.get(reverse("chore_list")), "NewName")
        self.assertContains(self.client.get(reverse("identity_pick")), "NewName")

    def test_rename_household_is_reflected_in_chore_list_and_identity_pick(self):
        h = Household.objects.create(name="Old House")
        m = Member.objects.create(household=h, name="M")
        Chore.objects.create(
            household=h, name="Dishes", cadence=Chore.Cadence.DAILY, current_holder=m
        )
        self.client.post(reverse("rename_household"), {"name": "New House"})
        h.refresh_from_db()
        self.assertEqual(h.name, "New House")

        session = self.client.session
        session["member_id"] = m.id
        session.save()
        self.assertContains(self.client.get(reverse("chore_list")), "New House")
        self.assertContains(self.client.get(reverse("identity_pick")), "New House")

    def test_remove_member_without_a_chore_deletes_them(self):
        h = Household.objects.create(name="H")
        keep = Member.objects.create(household=h, name="Keep")
        drop = Member.objects.create(household=h, name="Drop")
        resp = self.client.post(reverse("remove_member", args=[drop.id]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Member.objects.filter(pk=drop.pk).exists())
        self.assertTrue(Member.objects.filter(pk=keep.pk).exists())

    def test_remove_member_holding_a_chore_does_not_500_and_shows_a_message(self):
        h = Household.objects.create(name="H")
        holder = Member.objects.create(household=h, name="Holder")
        Chore.objects.create(
            household=h, name="Dishes", cadence=Chore.Cadence.DAILY, current_holder=holder
        )
        resp = self.client.post(
            reverse("remove_member", args=[holder.id]), follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Member.objects.filter(pk=holder.pk).exists())
        self.assertContains(resp, "currently hold")

    def test_management_flow_never_creates_a_second_household(self):
        h = Household.objects.create(name="H")
        self.client.post(reverse("add_member"), {"name": "A"})
        self.client.post(reverse("rename_household"), {"name": "Renamed"})
        self.assertEqual(Household.objects.count(), 1)

    def test_management_views_do_not_500_when_no_household_exists(self):
        self.assertEqual(self.client.get(reverse("household_manage")).status_code, 200)
        self.assertEqual(
            self.client.post(reverse("add_member"), {"name": "A"}, follow=True).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                reverse("rename_household"), {"name": "X"}, follow=True
            ).status_code,
            200,
        )
        self.assertEqual(Household.objects.count(), 0)
        self.assertEqual(Member.objects.count(), 0)


class ChoreManageTests(AuthClientMixin, TestCase):
    """The in-app chore management UI (issue #10)."""

    def setUp(self):
        self.h = Household.objects.create(name="H")
        self.alice = Member.objects.create(household=self.h, name="Alice")
        self.bob = Member.objects.create(household=self.h, name="Bob")

    def make_chore(self, name="Dishes", cadence=Chore.Cadence.DAILY, holder=None):
        return Chore.objects.create(
            household=self.h,
            name=name,
            cadence=cadence,
            current_holder=holder or self.alice,
        )

    def test_page_is_not_gated_by_require_identity(self):
        # No session identity -- the page must still render (admin-style CRUD).
        resp = self.client.get(reverse("chore_manage"))
        self.assertEqual(resp.status_code, 200)

    def test_page_lists_each_chore_with_its_cadence_label_and_holder(self):
        self.make_chore(
            name="Take out trash", cadence=Chore.Cadence.WEEKLY, holder=self.bob
        )
        resp = self.client.get(reverse("chore_manage"))
        self.assertContains(resp, "Take out trash")
        self.assertContains(resp, "Bob")
        # Cadence <select> is populated from Chore.Cadence, not free text.
        for _, label in Chore.Cadence.choices:
            self.assertContains(resp, "<option", status_code=200)
            self.assertContains(resp, label)
        # The row carries the chore, its cadence and its holder in context.
        listed = {c.name: c for c in resp.context["chores"]}
        self.assertEqual(listed["Take out trash"].cadence, Chore.Cadence.WEEKLY)
        self.assertEqual(listed["Take out trash"].current_holder, self.bob)

    def test_add_chore_creates_it_and_it_shows_in_manage_and_chore_list(self):
        resp = self.client.post(
            reverse("add_chore"),
            {
                "name": "Sweep floors",
                "cadence": Chore.Cadence.MONTHLY,
                "current_holder": self.bob.id,
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        chore = Chore.objects.get(name="Sweep floors")
        self.assertEqual(chore.household, self.h)
        self.assertEqual(chore.cadence, Chore.Cadence.MONTHLY)
        self.assertEqual(chore.current_holder, self.bob)
        # Visible on the management page...
        self.assertContains(self.client.get(reverse("chore_manage")), "Sweep floors")
        # ...and in chore_list (which is require_identity-gated).
        self.login_as(self.alice)
        self.assertContains(self.client.get(reverse("chore_list")), "Sweep floors")

    def test_add_chore_rejects_a_blank_name(self):
        resp = self.client.post(
            reverse("add_chore"),
            {"name": "   ", "cadence": Chore.Cadence.DAILY, "current_holder": self.alice.id},
            follow=True,
        )
        self.assertEqual(Chore.objects.count(), 0)
        self.assertContains(resp, "blank")

    def test_add_chore_rejects_a_free_text_cadence(self):
        resp = self.client.post(
            reverse("add_chore"),
            {
                "name": "Sweep floors",
                "cadence": "fortnightly",
                "current_holder": self.alice.id,
            },
            follow=True,
        )
        self.assertEqual(Chore.objects.count(), 0)
        self.assertContains(resp, "cadence")

    def test_add_chore_rejects_a_holder_from_another_household(self):
        other = Household.objects.create(name="Other")
        outsider = Member.objects.create(household=other, name="Outsider")
        resp = self.client.post(
            reverse("add_chore"),
            {
                "name": "Sweep floors",
                "cadence": Chore.Cadence.DAILY,
                "current_holder": outsider.id,
            },
            follow=True,
        )
        self.assertEqual(Chore.objects.count(), 0)
        self.assertContains(resp, "holder")

    def test_edit_chore_updates_name_cadence_and_holder(self):
        chore = self.make_chore(
            name="Old name", cadence=Chore.Cadence.DAILY, holder=self.alice
        )
        resp = self.client.post(
            reverse("edit_chore", args=[chore.id]),
            {
                "name": "New name",
                "cadence": Chore.Cadence.WEEKLY,
                "current_holder": self.bob.id,
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        chore.refresh_from_db()
        self.assertEqual(chore.name, "New name")
        self.assertEqual(chore.cadence, Chore.Cadence.WEEKLY)
        self.assertEqual(chore.current_holder, self.bob)

    def test_edit_chore_will_not_set_a_holder_from_another_household(self):
        other = Household.objects.create(name="Other")
        outsider = Member.objects.create(household=other, name="Outsider")
        chore = self.make_chore(holder=self.alice)
        self.client.post(
            reverse("edit_chore", args=[chore.id]),
            {
                "name": "Dishes",
                "cadence": Chore.Cadence.DAILY,
                "current_holder": outsider.id,
            },
        )
        chore.refresh_from_db()
        self.assertEqual(chore.current_holder, self.alice)

    def test_delete_chore_removes_it_without_protectederror(self):
        # A member currently holds this chore; deleting the chore still just
        # works -- nothing points at Chore with on_delete=PROTECT.
        chore = self.make_chore(holder=self.alice)
        resp = self.client.post(reverse("delete_chore", args=[chore.id]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Chore.objects.filter(pk=chore.pk).exists())
        self.assertTrue(Member.objects.filter(pk=self.alice.pk).exists())

    def test_create_form_degrades_gracefully_when_the_household_has_no_members(self):
        self.alice.delete()
        self.bob.delete()
        resp = self.client.get(reverse("chore_manage"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "no members")
        # A POST anyway does not crash and creates nothing.
        resp = self.client.post(
            reverse("add_chore"),
            {"name": "Sweep floors", "cadence": Chore.Cadence.DAILY, "current_holder": ""},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Chore.objects.count(), 0)

    def test_no_page_here_creates_a_second_household(self):
        self.client.post(
            reverse("add_chore"),
            {
                "name": "Sweep floors",
                "cadence": Chore.Cadence.DAILY,
                "current_holder": self.alice.id,
            },
        )
        self.client.post(
            reverse("edit_chore", args=[Chore.objects.get().id]),
            {
                "name": "Sweep floors",
                "cadence": Chore.Cadence.WEEKLY,
                "current_holder": self.bob.id,
            },
        )
        self.assertEqual(Household.objects.count(), 1)

    def test_management_views_do_not_500_when_no_household_exists(self):
        Chore.objects.all().delete()
        Member.objects.all().delete()
        Household.objects.all().delete()
        self.assertEqual(self.client.get(reverse("chore_manage")).status_code, 200)
        self.assertEqual(
            self.client.post(
                reverse("add_chore"),
                {"name": "X", "cadence": Chore.Cadence.DAILY, "current_holder": "1"},
                follow=True,
            ).status_code,
            200,
        )
        self.assertEqual(Household.objects.count(), 0)
        self.assertEqual(Chore.objects.count(), 0)
