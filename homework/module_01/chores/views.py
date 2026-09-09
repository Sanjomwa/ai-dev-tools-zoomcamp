from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .guards import require_identity
from .models import Chore, Household, Member


def identity_pick(request):
    # Exempt from require_identity (issue #4) — this is the page the guard
    # redirects TO, so guarding it would loop.
    household = Household.objects.first()
    members = household.members.all() if household else []
    return render(request, "chores/identity_pick.html", {"household": household, "members": members})


def pick_identity(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    request.session["member_id"] = member.id
    return redirect("chore_list")


def switch_identity(request):
    # Leave the current identity (issue #11): drop the single session key the
    # app uses for "who am I" and send the user back to the picker. Mirrors
    # pick_identity's plain-GET style. Not guarded with require_identity —
    # clearing an identity you might not have is a harmless no-op, and the
    # redirect target is identity_pick either way.
    request.session.pop("member_id", None)
    return redirect("identity_pick")


@require_identity
def chore_list(request):
    household = Household.objects.first()
    # `household` is only falsy if there is no Household at all, in which case
    # there are no Members and require_identity already redirected. The branch
    # is kept as belt-and-braces so a direct call can't raise.
    chores = household.chores.select_related("current_holder").all() if household else []
    # The template compares this against each chore.current_holder_id to decide
    # whether to render an actionable mark-done control (issue #8's 403 is the
    # server-side backstop). require_identity guarantees the key is set.
    return render(
        request,
        "chores/chore_list.html",
        {
            "household": household,
            "chores": chores,
            "current_member_id": request.session["member_id"],
        },
    )


@require_identity
@require_POST
def mark_done(request, chore_id):
    chore = get_object_or_404(Chore, pk=chore_id)
    # Only the current holder may mark their own chore done (issue #8).
    # require_identity guarantees member_id is set and points at a real Member.
    if request.session["member_id"] != chore.current_holder_id:
        return HttpResponseForbidden("Only the current holder can mark this chore done.")
    # "Next in rotation" is the following entry in the household's Meta-ordered
    # member list, wrapping to the first. Computed by position in that list, not
    # by `order + 1`: `order` can have gaps once a member is deleted, and a
    # single-member household must wrap to itself.
    members = list(chore.household.members.all())
    member_ids = [member.pk for member in members]
    next_index = (member_ids.index(chore.current_holder_id) + 1) % len(members)

    chore.current_holder = members[next_index]
    chore.last_completed_at = timezone.now()
    chore.save()
    return redirect("chore_list")


# --- Household / member management (issue #9) -------------------------------
#
# Not guarded with require_identity: this UI has to work before any member
# exists, so that a brand-new household can be populated from zero. It manages
# the single existing household only (decisions.md #6) — no page here creates a
# Household, and there is deliberately no form to do so.


def household_manage(request):
    household = Household.objects.first()
    members = household.members.all() if household else []
    return render(
        request,
        "chores/household_manage.html",
        {"household": household, "members": members},
    )


@require_POST
def rename_household(request):
    household = Household.objects.first()
    if household is None:
        messages.error(request, "No household has been set up yet.")
        return redirect("household_manage")
    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Household name can't be blank.")
        return redirect("household_manage")
    household.name = name
    household.save()
    messages.success(request, "Household renamed.")
    return redirect("household_manage")


@require_POST
def add_member(request):
    household = Household.objects.first()
    if household is None:
        messages.error(request, "No household has been set up yet.")
        return redirect("household_manage")
    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Member name can't be blank.")
        return redirect("household_manage")
    # Don't pass order= — Member.save() assigns it by creation order, placing
    # the new member at the end of the rotation.
    Member.objects.create(household=household, name=name)
    messages.success(request, f'Added "{name}".')
    return redirect("household_manage")


@require_POST
def rename_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Member name can't be blank.")
        return redirect("household_manage")
    member.name = name
    member.save()
    messages.success(request, "Member renamed.")
    return redirect("household_manage")


@require_POST
def remove_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    try:
        member.delete()
    except ProtectedError:
        # Chore.current_holder is on_delete=PROTECT: a member currently holding
        # a chore can't be removed. Surface it as a readable message instead of
        # a 500.
        messages.error(
            request,
            f'Can\'t remove "{member.name}" — they currently hold one or more '
            "chores. Mark those chores done (or reassign them) first.",
        )
        return redirect("household_manage")
    messages.success(request, f'Removed "{member.name}".')
    return redirect("household_manage")
