from django.urls import path

from . import views

urlpatterns = [
    path("", views.identity_pick, name="identity_pick"),
    path("identity/<int:member_id>/pick/", views.pick_identity, name="pick_identity"),
    path("identity/switch/", views.switch_identity, name="switch_identity"),
    path("chores/", views.chore_list, name="chore_list"),
    path("chores/<int:chore_id>/done/", views.mark_done, name="mark_done"),
    path("chores/manage/", views.chore_manage, name="chore_manage"),
    path("chores/manage/add/", views.add_chore, name="add_chore"),
    path("chores/manage/<int:chore_id>/edit/", views.edit_chore, name="edit_chore"),
    path("chores/manage/<int:chore_id>/delete/", views.delete_chore, name="delete_chore"),
    path("household/", views.household_manage, name="household_manage"),
    path("household/rename/", views.rename_household, name="rename_household"),
    path("household/members/add/", views.add_member, name="add_member"),
    path("household/members/<int:member_id>/rename/", views.rename_member, name="rename_member"),
    path("household/members/<int:member_id>/remove/", views.remove_member, name="remove_member"),
]
