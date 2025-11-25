"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""

    list_display = ('email', 'name', 'role', 'school', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'school')
    search_fields = ('email', 'name')
    ordering = ('name',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'school', 'role', 'subjects')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Settings', {'fields': ('settings',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'role', 'school'),
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for audit log."""

    list_display = ('user', 'action', 'entity_type', 'entity_id', 'created_at')
    list_filter = ('action', 'entity_type', 'created_at')
    search_fields = ('user__email', 'entity_type', 'action')
    readonly_fields = ('id', 'user', 'action', 'entity_type', 'entity_id', 'details', 'ip_address', 'user_agent', 'created_at')
    ordering = ('-created_at',)
