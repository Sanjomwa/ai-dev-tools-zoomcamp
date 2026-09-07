from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Household, Member


def identity_pick(request):
    household = Household.objects.first()
    members = household.members.all() if household else []
    return render(request, "chores/identity_pick.html", {"household": household, "members": members})


def pick_identity(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    request.session["member_id"] = member.id
    return redirect("chore_list")


def chore_list(request):
    # Stub per issue #3's Constraints — real implementation is issue #5.
    return HttpResponse("Chore list — not yet implemented (see issue #5).")
