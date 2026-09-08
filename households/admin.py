from django.contrib import admin

from .models import Household, Member


class MemberInline(admin.TabularInline):
    model = Member
    extra = 0
    fields = ["name", "completed_turns", "owed_turns", "last_assigned_at"]
    readonly_fields = ["last_assigned_at"]


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    inlines = [MemberInline]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "household",
        "completed_turns",
        "owed_turns",
        "joined_at",
        "last_assigned_at",
    ]
    list_filter = ["household"]
