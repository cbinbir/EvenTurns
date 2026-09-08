from django.contrib import admin

from .models import Assignment, Chore, Skip


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ["member", "status", "assigned_at", "completed_at"]
    readonly_fields = ["assigned_at"]


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ["name", "household", "chore_type", "frequency", "created_at"]
    list_filter = ["household", "chore_type"]
    inlines = [AssignmentInline]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["chore", "member", "status", "assigned_at", "completed_at"]
    list_filter = ["status", "chore__household"]


@admin.register(Skip)
class SkipAdmin(admin.ModelAdmin):
    list_display = ["assignment", "skipped_at"]
    readonly_fields = ["skipped_at"]
