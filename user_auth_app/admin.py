from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'id', 'email', 'is_staff', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'email',)