"""
Admin configuration for students app.
"""
from django.contrib import admin
from .models import (
    StudentProfile, StudentCondition, AdaptationSettings,
    SubjectAdaptation, AdaptationTemplate
)


class StudentConditionInline(admin.TabularInline):
    """Inline for student conditions."""
    model = StudentCondition
    extra = 1


class AdaptationSettingsInline(admin.StackedInline):
    """Inline for adaptation settings."""
    model = AdaptationSettings
    can_delete = False
    fieldsets = (
        ('Reading & Language', {
            'fields': (
                'reading_year_level', 'max_sentence_length', 'vocabulary_simplification',
                'literal_language_mode', 'literal_language_intensity', 'syllable_breaking',
                'key_word_highlighting'
            )
        }),
        ('Visual & Layout', {
            'fields': (
                'font', 'font_size', 'line_spacing', 'letter_spacing',
                'background_colour', 'text_colour', 'visual_density'
            )
        }),
        ('Structure & Chunking', {
            'fields': (
                'questions_per_section', 'numbered_steps', 'progress_indicators',
                'section_breaks', 'reference_panels', 'scaffolded_answers', 'explicit_instructions'
            )
        }),
        ('Audio', {
            'fields': ('tts_enabled', 'tts_speed', 'tts_voice', 'word_highlighting')
        }),
        ('Emotional & Pacing', {
            'fields': ('timer_display', 'feedback_style', 'encouragement_prompts', 'anxiety_reduction')
        }),
        ('Translation', {
            'fields': ('first_language', 'translation_mode')
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin for student profiles."""

    list_display = ('display_name', 'student_identifier', 'school', 'year_group', 'is_active', 'created_at')
    list_filter = ('school', 'year_group', 'is_active')
    search_fields = ('display_name', 'student_identifier')
    ordering = ('display_name',)
    inlines = [StudentConditionInline, AdaptationSettingsInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('school')


@admin.register(StudentCondition)
class StudentConditionAdmin(admin.ModelAdmin):
    """Admin for student conditions."""

    list_display = ('student_profile', 'condition_type', 'severity', 'diagnosed', 'created_at')
    list_filter = ('condition_type', 'severity', 'diagnosed')
    search_fields = ('student_profile__display_name', 'student_profile__student_identifier')


@admin.register(AdaptationSettings)
class AdaptationSettingsAdmin(admin.ModelAdmin):
    """Admin for adaptation settings."""

    list_display = ('student_profile', 'reading_year_level', 'font', 'created_at')
    list_filter = ('font', 'background_colour', 'tts_enabled')
    search_fields = ('student_profile__display_name',)


@admin.register(SubjectAdaptation)
class SubjectAdaptationAdmin(admin.ModelAdmin):
    """Admin for subject-specific adaptations."""

    list_display = ('student_profile', 'subject', 'created_at')
    list_filter = ('subject',)
    search_fields = ('student_profile__display_name',)


@admin.register(AdaptationTemplate)
class AdaptationTemplateAdmin(admin.ModelAdmin):
    """Admin for adaptation templates."""

    list_display = ('name', 'school', 'is_global', 'created_at')
    list_filter = ('is_global', 'school')
    search_fields = ('name', 'description')
