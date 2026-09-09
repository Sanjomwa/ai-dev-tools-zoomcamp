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


@require_identity
def chore_list(request):
    household = Household.objects.first()
    # `household` is only falsy if there is no Household at all, in which case
    # there are no Members and require_identity already redirected. The branch
    # is kept as belt-and-braces so a direct call can't raise.
    chores = household.chores.select_related("current_holder").all() if household else []
    return render(request, "chores/chore_list.html", {"chores": chores})


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
