"""
Admin configuration for adaptations app.
"""
from django.contrib import admin
from .models import PromptTemplate, SubjectTerms, ContentRule, IdiomDictionary


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    """Admin for prompt templates."""

    list_display = ('condition_type', 'version', 'is_active', 'created_at', 'updated_at')
    list_filter = ('condition_type', 'is_active')
    search_fields = ('condition_type', 'prompt_section')
    ordering = ('condition_type', '-version')

    fieldsets = (
        (None, {'fields': ('condition_type', 'version', 'is_active')}),
        ('Prompt Content', {'fields': ('prompt_section', 'intensive_prompt')}),
        ('Notes', {'fields': ('notes',)}),
    )


@admin.register(SubjectTerms)
class SubjectTermsAdmin(admin.ModelAdmin):
    """Admin for subject terms."""

    list_display = ('subject', 'term_count', 'created_at', 'updated_at')
    search_fields = ('subject',)
    ordering = ('subject',)

    def term_count(self, obj):
        return len(obj.terms)
    term_count.short_description = 'Terms'


@admin.register(ContentRule)
class ContentRuleAdmin(admin.ModelAdmin):
    """Admin for content rules."""

    list_display = ('rule_type', 'is_active', 'created_at')
    list_filter = ('is_active',)
    ordering = ('rule_type',)


@admin.register(IdiomDictionary)
class IdiomDictionaryAdmin(admin.ModelAdmin):
    """Admin for idiom dictionary."""

    list_display = ('idiom', 'literal_meaning', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('idiom', 'literal_meaning')
    ordering = ('idiom',)
