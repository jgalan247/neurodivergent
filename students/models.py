"""
Student profile and adaptation settings models for AdaptEd.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class StudentProfile(models.Model):
    """Core student profile containing basic information."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='students'
    )
    student_identifier = models.CharField(
        max_length=100,
        help_text='School\'s student ID (anonymised)'
    )
    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='First name only for privacy'
    )
    year_group = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(13)]
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_students'
    )
    notes = models.TextField(blank=True, help_text='General notes about the student')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'
        unique_together = ['school', 'student_identifier']
        ordering = ['display_name', 'student_identifier']

    def __str__(self):
        return self.display_name or self.student_identifier


class StudentCondition(models.Model):
    """Conditions/diagnoses associated with a student."""

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

    class Severity(models.TextChoices):
        MILD = 'mild', 'Mild'
        MODERATE = 'moderate', 'Moderate'
        SIGNIFICANT = 'significant', 'Significant'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='conditions'
    )
    condition_type = models.CharField(max_length=50, choices=ConditionType.choices)
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.MODERATE
    )
    diagnosed = models.BooleanField(
        default=False,
        help_text='Whether this is a formal diagnosis'
    )
    notes = models.TextField(blank=True)
    first_language = models.CharField(
        max_length=50,
        blank=True,
        help_text='For EAL condition - student\'s first language'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_conditions'
        unique_together = ['student_profile', 'condition_type']

    def __str__(self):
        return f"{self.student_profile} - {self.get_condition_type_display()}"


class AdaptationSettings(models.Model):
    """Detailed adaptation settings for a student profile."""

    class FontChoice(models.TextChoices):
        ARIAL = 'arial', 'Arial'
        VERDANA = 'verdana', 'Verdana'
        OPEN_DYSLEXIC = 'opendyslexic', 'OpenDyslexic'
        LEXIE_READABLE = 'lexie', 'Lexie Readable'
        COMIC_SANS = 'comic_sans', 'Comic Sans MS'

    class BackgroundColour(models.TextChoices):
        WHITE = 'white', 'White'
        CREAM = 'cream', 'Cream (#FFF8E7)'
        LIGHT_YELLOW = 'light_yellow', 'Light Yellow (#FFFACD)'
        LIGHT_BLUE = 'light_blue', 'Light Blue (#E6F3FF)'
        LIGHT_PINK = 'light_pink', 'Light Pink (#FFE4E1)'
        LIGHT_GREEN = 'light_green', 'Light Green (#E8F5E9)'

    class TextColour(models.TextChoices):
        BLACK = 'black', 'Black (#000000)'
        DARK_GREY = 'dark_grey', 'Dark Grey (#333333)'
        NAVY = 'navy', 'Navy (#1a1a2e)'

    class TimerDisplay(models.TextChoices):
        HIDE = 'hide', 'Hidden'
        SHOW = 'show', 'Visible'
        WARNINGS = 'warnings', 'Visible with warnings'

    class FeedbackStyle(models.TextChoices):
        NEUTRAL = 'neutral', 'Neutral'
        ENCOURAGING = 'encouraging', 'Encouraging'
        MINIMAL = 'minimal', 'Minimal'

    class TranslationMode(models.TextChoices):
        NONE = 'none', 'No translation'
        GLOSSARY = 'glossary', 'Bilingual glossary only'
        FULL = 'full', 'Full translation'
        SIDE_BY_SIDE = 'side_by_side', 'Side-by-side bilingual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_profile = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='adaptation_settings'
    )

    # Reading & Language settings
    reading_year_level = models.IntegerField(
        default=8,
        validators=[MinValueValidator(3), MaxValueValidator(13)],
        help_text='Target reading level (year group)'
    )
    max_sentence_length = models.IntegerField(
        default=15,
        validators=[MinValueValidator(6), MaxValueValidator(25)],
        help_text='Maximum words per sentence'
    )
    vocabulary_simplification = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='1=maximum simplification, 10=no simplification'
    )
    literal_language_mode = models.BooleanField(
        default=False,
        help_text='Remove idioms and figurative language'
    )
    literal_language_intensity = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='How aggressively to replace figurative language'
    )
    syllable_breaking = models.BooleanField(
        default=False,
        help_text='Add syllable breaks to longer words'
    )
    key_word_highlighting = models.BooleanField(
        default=True,
        help_text='Bold action words and key information'
    )

    # Visual & Layout settings
    font = models.CharField(
        max_length=50,
        choices=FontChoice.choices,
        default=FontChoice.ARIAL
    )
    font_size = models.IntegerField(
        default=14,
        validators=[MinValueValidator(12), MaxValueValidator(24)]
    )
    line_spacing = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.5,
        validators=[MinValueValidator(1.0), MaxValueValidator(3.0)]
    )
    letter_spacing = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        help_text='Percentage increase in letter spacing'
    )
    background_colour = models.CharField(
        max_length=20,
        choices=BackgroundColour.choices,
        default=BackgroundColour.CREAM
    )
    text_colour = models.CharField(
        max_length=20,
        choices=TextColour.choices,
        default=TextColour.DARK_GREY
    )
    visual_density = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='1=maximum spacing, 10=compact'
    )

    # Structure & Chunking settings
    questions_per_section = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    numbered_steps = models.BooleanField(
        default=True,
        help_text='Always number multi-step instructions'
    )
    progress_indicators = models.BooleanField(
        default=True,
        help_text='Show question X of Y indicators'
    )
    section_breaks = models.BooleanField(
        default=True,
        help_text='Add clear section breaks'
    )
    reference_panels = models.BooleanField(
        default=False,
        help_text='Include reference boxes for formulas/info'
    )
    scaffolded_answers = models.BooleanField(
        default=False,
        help_text='Provide step-by-step answer templates'
    )
    explicit_instructions = models.BooleanField(
        default=True,
        help_text='Make all instructions completely explicit'
    )

    # Audio settings
    tts_enabled = models.BooleanField(
        default=False,
        help_text='Enable text-to-speech'
    )
    tts_speed = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(2.0)]
    )
    tts_voice = models.CharField(max_length=50, default='default')
    word_highlighting = models.BooleanField(
        default=False,
        help_text='Highlight words as they are read'
    )

    # Emotional & Pacing settings
    timer_display = models.CharField(
        max_length=20,
        choices=TimerDisplay.choices,
        default=TimerDisplay.SHOW
    )
    feedback_style = models.CharField(
        max_length=20,
        choices=FeedbackStyle.choices,
        default=FeedbackStyle.NEUTRAL
    )
    encouragement_prompts = models.BooleanField(
        default=False,
        help_text='Include encouraging messages'
    )
    anxiety_reduction = models.BooleanField(
        default=False,
        help_text='Use calming language and formatting'
    )

    # Translation settings
    first_language = models.CharField(
        max_length=10,
        default='en',
        help_text='ISO language code for first language'
    )
    translation_mode = models.CharField(
        max_length=30,
        choices=TranslationMode.choices,
        default=TranslationMode.NONE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'adaptation_settings'

    def __str__(self):
        return f"Settings for {self.student_profile}"


class SubjectAdaptation(models.Model):
    """Subject-specific overrides for adaptation settings."""

    class Subject(models.TextChoices):
        ENGLISH = 'english', 'English'
        MATHEMATICS = 'mathematics', 'Mathematics'
        SCIENCE = 'science', 'Science'
        HISTORY = 'history', 'History'
        GEOGRAPHY = 'geography', 'Geography'
        LANGUAGES = 'languages', 'Modern Languages'
        ART = 'art', 'Art & Design'
        MUSIC = 'music', 'Music'
        PE = 'pe', 'Physical Education'
        COMPUTING = 'computing', 'Computing'
        DT = 'dt', 'Design & Technology'
        RE = 're', 'Religious Education'
        PSHE = 'pshe', 'PSHE'
        OTHER = 'other', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='subject_adaptations'
    )
    subject = models.CharField(max_length=50, choices=Subject.choices)
    override_settings = models.JSONField(
        default=dict,
        help_text='Only the settings that differ from core settings'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subject_adaptations'
        unique_together = ['student_profile', 'subject']

    def __str__(self):
        return f"{self.student_profile} - {self.get_subject_display()}"


class AdaptationTemplate(models.Model):
    """Pre-built adaptation templates for common profiles."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='adaptation_templates',
        help_text='Null for global templates'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    conditions = models.JSONField(
        default=list,
        help_text='List of condition types this template addresses'
    )
    settings = models.JSONField(
        default=dict,
        help_text='Full settings object'
    )
    is_global = models.BooleanField(
        default=False,
        help_text='Available to all schools'
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'adaptation_templates'
        ordering = ['name']

    def __str__(self):
        return self.name
