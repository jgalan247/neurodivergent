"""
Assessment models for AdaptEd.
"""
import uuid
from django.db import models


class Assessment(models.Model):
    """Original assessment uploaded by teachers."""

    class FileType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        DOCX = 'docx', 'Word Document'
        IMAGE = 'image', 'Image'

    class Status(models.TextChoices):
        UPLOADED = 'uploaded', 'Uploaded'
        PROCESSING = 'processing', 'Processing'
        READY = 'ready', 'Ready'
        ERROR = 'error', 'Error'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assessments'
    )
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=50)
    year_group = models.IntegerField(null=True, blank=True)

    # File information
    original_file = models.FileField(upload_to='assessments/originals/')
    original_file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.PDF
    )

    # Extracted content
    extracted_text = models.TextField(blank=True)
    page_count = models.IntegerField(default=1)

    # Content flags (auto-detected or manually set)
    content_flags = models.JSONField(
        default=dict,
        blank=True,
        help_text='Flags like {quotations: true, code: false, maths: true}'
    )

    # Protected terms
    protected_terms = models.JSONField(
        default=list,
        blank=True,
        help_text='Subject-specific terms to preserve'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED
    )
    error_message = models.TextField(blank=True)

    # Metadata
    description = models.TextField(blank=True)
    instructions = models.TextField(
        blank=True,
        help_text='Special instructions for adaptation'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assessments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.subject})"

    @property
    def adaptation_count(self):
        return self.adapted_versions.count()

    @property
    def pending_review_count(self):
        return self.adapted_versions.filter(status='pending').count()

    @property
    def approved_count(self):
        return self.adapted_versions.filter(status='approved').count()


def adapted_assessment_upload_path(instance, filename):
    """Generate upload path for adapted assessment files."""
    return f'assessments/adapted/{instance.assessment.id}/{instance.id}/{filename}'


class AdaptedAssessment(models.Model):
    """Adapted version of an assessment for a specific student or template."""

    class Status(models.TextChoices):
        GENERATING = 'generating', 'Generating'
        PENDING = 'pending', 'Pending Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        NEEDS_EDIT = 'needs_edit', 'Needs Editing'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='adapted_versions'
    )

    # Either for a specific student or from a template
    student_profile = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='adapted_assessments'
    )
    adaptation_template = models.ForeignKey(
        'students.AdaptationTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Adapted content
    adapted_content = models.TextField(help_text='The AI-adapted content in markdown/HTML')

    # AI metadata
    adaptation_prompt = models.TextField(blank=True, help_text='The prompt used for adaptation')
    ai_model = models.CharField(max_length=50, blank=True, help_text='Model used for adaptation')
    ai_tokens_used = models.IntegerField(default=0)
    adaptation_time_seconds = models.FloatField(default=0)

    # Validation results
    validation_results = models.JSONField(
        default=dict,
        blank=True,
        help_text='Results from automated validation'
    )
    validation_warnings = models.JSONField(default=list, blank=True)

    # Review workflow
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.GENERATING
    )
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_adaptations'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    # Manual edits
    manually_edited = models.BooleanField(default=False)
    edited_content = models.TextField(blank=True, help_text='Teacher-edited version')

    # Output files
    output_pdf = models.FileField(
        upload_to=adapted_assessment_upload_path,
        blank=True
    )
    output_docx = models.FileField(
        upload_to=adapted_assessment_upload_path,
        blank=True
    )
    output_html = models.TextField(blank=True)

    # Audio version
    audio_file = models.FileField(
        upload_to=adapted_assessment_upload_path,
        blank=True
    )
    audio_generated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'adapted_assessments'
        ordering = ['-created_at']

    def __str__(self):
        target = self.student_profile or self.adaptation_template
        return f"{self.assessment.title} → {target}"

    @property
    def final_content(self):
        """Return the edited content if edited, otherwise the original adapted content."""
        return self.edited_content if self.manually_edited else self.adapted_content

    def get_conditions_display(self):
        """Get a display string of conditions this adaptation addresses."""
        if self.student_profile:
            return ', '.join([
                c.get_condition_type_display()
                for c in self.student_profile.conditions.all()
            ])
        elif self.adaptation_template:
            return ', '.join(self.adaptation_template.conditions)
        return ''
