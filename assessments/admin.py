"""
Admin configuration for assessments app.
"""
from django.contrib import admin
from .models import Assessment, AdaptedAssessment


class AdaptedAssessmentInline(admin.TabularInline):
    """Inline for adapted versions."""
    model = AdaptedAssessment
    extra = 0
    readonly_fields = ('id', 'student_profile', 'status', 'created_at')
    fields = ('student_profile', 'status', 'reviewed_by', 'created_at')
    can_delete = False
    show_change_link = True


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin for assessments."""

    list_display = ('title', 'subject', 'year_group', 'school', 'status', 'adaptation_count', 'created_at')
    list_filter = ('status', 'subject', 'school', 'year_group')
    search_fields = ('title', 'subject', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'extracted_text', 'page_count', 'created_at', 'updated_at')
    inlines = [AdaptedAssessmentInline]

    fieldsets = (
        (None, {'fields': ('title', 'subject', 'year_group', 'school', 'created_by')}),
        ('File', {'fields': ('original_file', 'original_file_type', 'status', 'error_message')}),
        ('Content', {'fields': ('extracted_text', 'page_count', 'content_flags', 'protected_terms')}),
        ('Metadata', {'fields': ('description', 'instructions', 'created_at', 'updated_at')}),
    )

    def adaptation_count(self, obj):
        return obj.adaptation_count
    adaptation_count.short_description = 'Adaptations'


@admin.register(AdaptedAssessment)
class AdaptedAssessmentAdmin(admin.ModelAdmin):
    """Admin for adapted assessments."""

    list_display = ('assessment', 'student_profile', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status', 'ai_model', 'manually_edited')
    search_fields = ('assessment__title', 'student_profile__display_name')
    ordering = ('-created_at',)
    readonly_fields = (
        'id', 'adapted_content', 'adaptation_prompt', 'ai_model',
        'ai_tokens_used', 'adaptation_time_seconds', 'validation_results',
        'validation_warnings', 'created_at', 'updated_at'
    )

    fieldsets = (
        (None, {'fields': ('assessment', 'student_profile', 'adaptation_template', 'status')}),
        ('Content', {'fields': ('adapted_content', 'manually_edited', 'edited_content')}),
        ('AI Metadata', {'fields': ('adaptation_prompt', 'ai_model', 'ai_tokens_used', 'adaptation_time_seconds')}),
        ('Validation', {'fields': ('validation_results', 'validation_warnings')}),
        ('Review', {'fields': ('reviewed_by', 'reviewed_at', 'review_notes')}),
        ('Output Files', {'fields': ('output_pdf', 'output_docx', 'audio_file', 'audio_generated')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
