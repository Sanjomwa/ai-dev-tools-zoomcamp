from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .guards import require_identity
from .models import Household, Member


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


# --- STUB: issue #6 (mark-done action) ---------------------------------------
# Real behaviour (set last_completed_at to now, advance current_holder to the
# next member in rotation) is issue #6's scope and is intentionally not built
# here. This stub exists only so issue #4's session-identity guard can be
# applied to a real endpoint and its acceptance criteria verified now. It is
# POST-only and wrapped in the same require_identity decorator as chore_list.
@require_identity
@require_POST
def mark_done(request, chore_id):
    return HttpResponse("Mark-done not yet implemented, see issue #6.")
