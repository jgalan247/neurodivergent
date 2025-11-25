"""
School models for AdaptEd.
"""
import uuid
from django.db import models


class School(models.Model):
    """School entity that owns student profiles and assessments."""

    class SubscriptionTier(models.TextChoices):
        FREE = 'free', 'Free'
        BASIC = 'basic', 'Basic'
        PROFESSIONAL = 'professional', 'Professional'
        ENTERPRISE = 'enterprise', 'Enterprise'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, blank=True, help_text='Email domain for verification')
    subscription_tier = models.CharField(
        max_length=20,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.FREE
    )
    settings = models.JSONField(default=dict, blank=True)

    # Contact information
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)

    # Limits based on subscription
    max_students = models.IntegerField(default=50)
    max_assessments_per_month = models.IntegerField(default=100)
    max_adaptations_per_month = models.IntegerField(default=500)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'schools'
        ordering = ['name']

    def __str__(self):
        return self.name


class UsageTracking(models.Model):
    """Track monthly usage for billing and quotas."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='usage_records')
    month = models.DateField(help_text='First day of the month')
    adaptations_count = models.IntegerField(default=0)
    ai_tokens_used = models.BigIntegerField(default=0)
    storage_bytes_used = models.BigIntegerField(default=0)
    assessments_uploaded = models.IntegerField(default=0)

    class Meta:
        db_table = 'usage_tracking'
        unique_together = ['school', 'month']
        ordering = ['-month']

    def __str__(self):
        return f"{self.school.name} - {self.month.strftime('%B %Y')}"
