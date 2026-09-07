from django.urls import path

from . import views

urlpatterns = [
    path("", views.identity_pick, name="identity_pick"),
    path("identity/<int:member_id>/pick/", views.pick_identity, name="pick_identity"),
    path("chores/", views.chore_list, name="chore_list"),
    path("chores/<int:chore_id>/done/", views.mark_done, name="mark_done"),
]
