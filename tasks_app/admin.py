from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'id',  'board', 'board_id', 'assignee', 'reviewer']
    list_filter = ['status', 'priority', 'board']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
