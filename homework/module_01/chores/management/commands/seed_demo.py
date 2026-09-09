"""Seed one household, its members, and a spread of chores for local dev / QA.

Run with ``uv run python manage.py seed_demo``. Intended for a fresh local
database so that ``/``, ``/chores/`` and the admin have something to show
without hand-creating rows.

Re-run behaviour: safe. Every row is created via ``get_or_create`` keyed on a
name, so a second run is a no-op -- it does NOT reset chores that were already
marked done (rotated holders and ``last_completed_at`` values are left alone).

Documented failure mode: if someone has manually created two members or two
chores with the same name in this household (there is no unique constraint on
``(household, name)``), ``get_or_create`` raises ``MultipleObjectsReturned``.
Delete the duplicate in admin and re-run.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from chores.models import Chore, Household, Member

HOUSEHOLD_NAME = "Demo Household"
MEMBER_NAMES = ["Ada", "Grace", "Linus", "Margaret"]

# (name, cadence, holder name, last_completed_at offset from now or None).
# The offsets are chosen to leave two chores overdue and three not, so the
# chore-list view renders both states. `None` means "never completed", which
# falls back to creation time and is therefore not overdue.
CHORE_SPECS = [
    ("Wash the dishes", Chore.Cadence.DAILY, "Ada", timedelta(hours=2)),
    ("Water the plants", Chore.Cadence.DAILY, "Grace", timedelta(hours=30)),
    ("Take out recycling", Chore.Cadence.WEEKLY, "Linus", None),
    ("Vacuum the living room", Chore.Cadence.WEEKLY, "Margaret", timedelta(days=9)),
    ("Deep-clean the fridge", Chore.Cadence.MONTHLY, "Ada", timedelta(days=10)),
]


class Command(BaseCommand):
    help = (
        "Create a demo household with members and chores for local dev/QA. "
        "Best run against a fresh database (the app's views render "
        "Household.objects.first(), so a pre-existing household wins). Safe to re-run."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        household, created = Household.objects.get_or_create(name=HOUSEHOLD_NAME)
        if not created:
            self.stdout.write(
                f'Household "{HOUSEHOLD_NAME}" already exists (pk={household.pk}); '
                "filling in any missing members/chores."
            )

        members = {}
        for name in MEMBER_NAMES:
            member, _ = Member.objects.get_or_create(household=household, name=name)
            members[name] = member

        now = timezone.now()
        new_chores = 0
        for name, cadence, holder_name, offset in CHORE_SPECS:
            _, chore_created = Chore.objects.get_or_create(
                household=household,
                name=name,
                defaults={
                    "cadence": cadence,
                    "current_holder": members[holder_name],
                    "last_completed_at": None if offset is None else now - offset,
                },
            )
            new_chores += int(chore_created)

        self.stdout.write(
            self.style.SUCCESS(
                f'"{HOUSEHOLD_NAME}": {len(members)} members, '
                f"{Chore.objects.filter(household=household).count()} chores "
                f"({new_chores} created this run)."
            )
        )
