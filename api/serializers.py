"""
API serializers for AdaptEd.
"""
from rest_framework import serializers
from accounts.models import User, AuditLog
from schools.models import School, UsageTracking
from students.models import (
    StudentProfile, StudentCondition, AdaptationSettings,
    SubjectAdaptation, AdaptationTemplate
)
from assessments.models import Assessment, AdaptedAssessment


# ============== Account Serializers ==============

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'role', 'school', 'subjects',
            'settings', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role', 'school', 'subjects']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ============== School Serializers ==============

class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model."""
    user_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            'id', 'name', 'domain', 'subscription_tier', 'settings',
            'max_students', 'max_assessments_per_month', 'max_adaptations_per_month',
            'is_active', 'user_count', 'student_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_user_count(self, obj):
        return obj.users.count()

    def get_student_count(self, obj):
        return obj.students.count()


class UsageTrackingSerializer(serializers.ModelSerializer):
    """Serializer for usage tracking."""

    class Meta:
        model = UsageTracking
        fields = [
            'id', 'school', 'month', 'adaptations_count',
            'ai_tokens_used', 'storage_bytes_used', 'assessments_uploaded'
        ]


# ============== Student Serializers ==============

class StudentConditionSerializer(serializers.ModelSerializer):
    """Serializer for student conditions."""
    condition_type_display = serializers.CharField(source='get_condition_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = StudentCondition
        fields = [
            'id', 'condition_type', 'condition_type_display',
            'severity', 'severity_display', 'diagnosed', 'notes',
            'first_language', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AdaptationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for adaptation settings."""

    class Meta:
        model = AdaptationSettings
        exclude = ['id', 'student_profile', 'created_at', 'updated_at']


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profiles."""
    conditions = StudentConditionSerializer(many=True, read_only=True)
    adaptation_settings = AdaptationSettingsSerializer(read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'school', 'school_name', 'student_identifier', 'display_name',
            'year_group', 'notes', 'is_active', 'conditions', 'adaptation_settings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating student profiles with conditions."""
    conditions = StudentConditionSerializer(many=True, required=False)
    adaptation_settings = AdaptationSettingsSerializer(required=False)

    class Meta:
        model = StudentProfile
        fields = [
            'student_identifier', 'display_name', 'year_group', 'notes',
            'conditions', 'adaptation_settings'
        ]

    def create(self, validated_data):
        conditions_data = validated_data.pop('conditions', [])
        settings_data = validated_data.pop('adaptation_settings', {})

        # Get school from request user
        request = self.context.get('request')
        validated_data['school'] = request.user.school
        validated_data['created_by'] = request.user

        student = StudentProfile.objects.create(**validated_data)

        # Create conditions
        for condition_data in conditions_data:
            StudentCondition.objects.create(student_profile=student, **condition_data)

        # Create or use default adaptation settings
        if settings_data:
            AdaptationSettings.objects.create(student_profile=student, **settings_data)
        else:
            AdaptationSettings.objects.create(student_profile=student)

        return student


class StudentProfileListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for student list views."""
    conditions = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'student_identifier', 'display_name', 'year_group',
            'is_active', 'conditions', 'created_at'
        ]

    def get_conditions(self, obj):
        return [
            {
                'type': c.condition_type,
                'display': c.get_condition_type_display(),
                'severity': c.severity
            }
            for c in obj.conditions.all()
        ]


class SubjectAdaptationSerializer(serializers.ModelSerializer):
    """Serializer for subject-specific adaptations."""

    class Meta:
        model = SubjectAdaptation
        fields = ['id', 'subject', 'override_settings', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdaptationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for adaptation templates."""

    class Meta:
        model = AdaptationTemplate
        fields = [
            'id', 'name', 'description', 'conditions', 'settings',
            'is_global', 'school', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ============== Assessment Serializers ==============

class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for assessments."""
    adaptation_count = serializers.IntegerField(read_only=True)
    pending_review_count = serializers.IntegerField(read_only=True)
    approved_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'subject', 'year_group', 'school',
            'original_file', 'original_file_type', 'extracted_text',
            'page_count', 'content_flags', 'protected_terms', 'status',
            'error_message', 'description', 'instructions',
            'adaptation_count', 'pending_review_count', 'approved_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'extracted_text', 'page_count', 'status', 'error_message',
            'created_at', 'updated_at'
        ]


class AssessmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating assessments."""

    class Meta:
        model = Assessment
        fields = [
            'title', 'subject', 'year_group', 'original_file',
            'content_flags', 'protected_terms', 'description', 'instructions'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['school'] = request.user.school
        validated_data['created_by'] = request.user

        # Detect file type
        file = validated_data.get('original_file')
        if file:
            filename = file.name.lower()
            if filename.endswith('.pdf'):
                validated_data['original_file_type'] = 'pdf'
            elif filename.endswith('.docx'):
                validated_data['original_file_type'] = 'docx'
            else:
                validated_data['original_file_type'] = 'image'

        return super().create(validated_data)


class AssessmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for assessment list views."""
    adaptation_count = serializers.IntegerField(read_only=True)
    pending_review_count = serializers.IntegerField(read_only=True)
    approved_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'subject', 'year_group', 'status',
            'adaptation_count', 'pending_review_count', 'approved_count',
            'created_at'
        ]


class AdaptedAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for adapted assessments."""
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    student_name = serializers.CharField(source='student_profile.display_name', read_only=True)
    conditions_display = serializers.SerializerMethodField()
    reviewed_by_name = serializers.CharField(source='reviewed_by.name', read_only=True)

    class Meta:
        model = AdaptedAssessment
        fields = [
            'id', 'assessment', 'assessment_title', 'student_profile', 'student_name',
            'adaptation_template', 'conditions_display', 'adapted_content',
            'ai_model', 'ai_tokens_used', 'adaptation_time_seconds',
            'validation_results', 'validation_warnings',
            'status', 'reviewed_by', 'reviewed_by_name', 'reviewed_at', 'review_notes',
            'manually_edited', 'edited_content',
            'output_pdf', 'output_docx', 'audio_generated',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'adapted_content', 'ai_model', 'ai_tokens_used',
            'adaptation_time_seconds', 'validation_results', 'validation_warnings',
            'created_at', 'updated_at'
        ]

    def get_conditions_display(self, obj):
        return obj.get_conditions_display()


class AdaptedAssessmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for adapted assessment list views."""
    student_name = serializers.CharField(source='student_profile.display_name', read_only=True)
    conditions = serializers.SerializerMethodField()

    class Meta:
        model = AdaptedAssessment
        fields = [
            'id', 'student_profile', 'student_name', 'conditions',
            'status', 'reviewed_at', 'created_at'
        ]

    def get_conditions(self, obj):
        if obj.student_profile:
            return [c.condition_type for c in obj.student_profile.conditions.all()]
        return []


class AdaptedAssessmentReviewSerializer(serializers.Serializer):
    """Serializer for reviewing adapted assessments."""
    action = serializers.ChoiceField(choices=['approve', 'reject', 'needs_edit'])
    review_notes = serializers.CharField(required=False, allow_blank=True)
    edited_content = serializers.CharField(required=False, allow_blank=True)


class GenerateAdaptationsSerializer(serializers.Serializer):
    """Serializer for generating adaptations."""
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    template_id = serializers.UUIDField(required=False)

    def validate(self, data):
        if not data.get('student_ids') and not data.get('template_id'):
            raise serializers.ValidationError(
                "Either student_ids or template_id must be provided"
            )
        return data
