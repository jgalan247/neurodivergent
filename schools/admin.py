"""
Admin configuration for schools app.
"""
from django.contrib import admin
from .models import School, UsageTracking


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    """Admin for School model."""

    list_display = ('name', 'domain', 'subscription_tier', 'is_active', 'created_at')
    list_filter = ('subscription_tier', 'is_active')
    search_fields = ('name', 'domain', 'contact_email')
    ordering = ('name',)

    fieldsets = (
        (None, {'fields': ('name', 'domain', 'is_active')}),
        ('Subscription', {'fields': ('subscription_tier', 'max_students', 'max_assessments_per_month', 'max_adaptations_per_month')}),
        ('Contact', {'fields': ('contact_email', 'phone', 'address')}),
        ('Settings', {'fields': ('settings',)}),
    )


@admin.register(UsageTracking)
class UsageTrackingAdmin(admin.ModelAdmin):
    """Admin for usage tracking."""

    list_display = ('school', 'month', 'adaptations_count', 'assessments_uploaded', 'ai_tokens_used')
    list_filter = ('month', 'school')
    ordering = ('-month',)
