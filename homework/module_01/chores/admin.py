from django.contrib import admin

from .models import Household, Member


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "household", "order")
    list_filter = ("household",)
