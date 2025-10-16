from django.contrib import admin

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'get_member_count']
    search_fields = ['title']
    list_filter = ['owner']
    filter_horizontal = ['members']
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Members'