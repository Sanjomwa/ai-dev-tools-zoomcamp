from django.contrib import admin

from .models import Chore, Household, Member


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "household", "order")
    list_filter = ("household",)


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("name", "household", "cadence", "current_holder", "last_completed_at")
    list_filter = ("household", "cadence")
