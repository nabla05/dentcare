from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Add our custom fields to the admin panel
    fieldsets = UserAdmin.fieldsets + (
        ('DentCare Profile', {
            'fields': ('role', 'phone', 'address', 'profile_photo')
        }),
    )
    list_display = ['username', 'email', 'get_full_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']