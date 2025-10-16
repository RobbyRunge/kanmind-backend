from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'status', 'priority', 'assignee', 'reviewer', 'due_date']
    list_filter = ['status', 'priority', 'board']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
