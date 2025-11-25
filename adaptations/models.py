"""
AI adaptation engine models and configuration for AdaptEd.
"""
import uuid
from django.db import models


class PromptTemplate(models.Model):
    """System prompts for each condition type."""

    class ConditionType(models.TextChoices):
        DYSLEXIA = 'dyslexia', 'Dyslexia'
        AUTISM = 'autism', 'Autism Spectrum Condition'
        ADHD = 'adhd', 'ADHD'
        DYSCALCULIA = 'dyscalculia', 'Dyscalculia'
        VISUAL_PROCESSING = 'visual_processing', 'Visual Processing Difficulties'
        AUDITORY_PROCESSING = 'auditory_processing', 'Auditory Processing Difficulties'
        WORKING_MEMORY = 'working_memory', 'Working Memory Difficulties'
        PROCESSING_SPEED = 'processing_speed', 'Slow Processing Speed'
        ANXIETY = 'anxiety', 'Test/Performance Anxiety'
        EAL = 'eal', 'English as Additional Language'
        # Special types for rules
        CORE_RULES = 'core_rules', 'Core Rules (Always Applied)'
        OUTPUT_FORMAT = 'output_format', 'Output Format Instructions'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    condition_type = models.CharField(max_length=50, choices=ConditionType.choices)
    prompt_section = models.TextField(help_text='The actual prompt instructions')
    intensive_prompt = models.TextField(
        blank=True,
        help_text='Additional instructions for significant severity'
    )
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text='Internal notes about this prompt')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prompt_templates'
        ordering = ['condition_type', '-version']
        unique_together = ['condition_type', 'version']

    def __str__(self):
        return f"{self.get_condition_type_display()} v{self.version}"


class SubjectTerms(models.Model):
    """Protected terms for each subject that should not be simplified."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=50, unique=True)
    terms = models.JSONField(
        default=list,
        help_text='List of protected terms for this subject'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subject_terms'
        verbose_name_plural = 'Subject terms'

    def __str__(self):
        return f"{self.subject} ({len(self.terms)} terms)"


class ContentRule(models.Model):
    """Rules for preserving specific content types."""

    class RuleType(models.TextChoices):
        PRESERVE_QUOTATIONS = 'preserve_quotations', 'Preserve Quotations'
        PRESERVE_MATHS = 'preserve_maths', 'Preserve Mathematical Notation'
        PRESERVE_CODE = 'preserve_code', 'Preserve Code'
        PRESERVE_DIAGRAMS = 'preserve_diagrams', 'Preserve Diagram References'
        PRESERVE_POETRY = 'preserve_poetry', 'Preserve Poetry Format'
        PRESERVE_SCRIPT = 'preserve_script', 'Preserve Script Format'
        NEVER_ANSWER = 'never_answer', 'Never Answer Questions'
        NEVER_ADD_INFO = 'never_add_info', 'Never Add New Information'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_type = models.CharField(max_length=50, choices=RuleType.choices, unique=True)
    prompt_text = models.TextField(help_text='The rule text to include in prompts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content_rules'

    def __str__(self):
        return self.get_rule_type_display()


class IdiomDictionary(models.Model):
    """Dictionary of idioms and their literal replacements for autism adaptations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idiom = models.CharField(max_length=255, unique=True)
    literal_meaning = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text='Category like weather, body, animals, etc.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'idiom_dictionary'
        ordering = ['idiom']

    def __str__(self):
        return f'"{self.idiom}" → "{self.literal_meaning}"'
