"""
API views for AdaptEd.
"""
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework import viewsets, status, generics, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout

from accounts.models import User
from schools.models import School
from students.models import (
    StudentProfile, StudentCondition, AdaptationSettings,
    SubjectAdaptation, AdaptationTemplate
)
from assessments.models import Assessment, AdaptedAssessment
from .serializers import (
    UserSerializer, UserCreateSerializer,
    SchoolSerializer,
    StudentProfileSerializer, StudentProfileCreateSerializer, StudentProfileListSerializer,
    StudentConditionSerializer, AdaptationSettingsSerializer,
    SubjectAdaptationSerializer, AdaptationTemplateSerializer,
    AssessmentSerializer, AssessmentCreateSerializer, AssessmentListSerializer,
    AdaptedAssessmentSerializer, AdaptedAssessmentListSerializer,
    AdaptedAssessmentReviewSerializer, GenerateAdaptationsSerializer
)
from .permissions import IsSchoolMember, IsSENCOOrAdmin


# ============== Authentication Views ==============

class LoginView(views.APIView):
    """Login view for email/password authentication."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(views.APIView):
    """Logout view."""

    def post(self, request):
        # Delete token if using token auth
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'Logged out successfully'})


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Get or update current user."""
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# ============== Dashboard Views ==============

class DashboardStatsView(views.APIView):
    """Get dashboard statistics for current user's school."""

    def get(self, request):
        school = request.user.school
        if not school:
            return Response({'error': 'No school associated'}, status=400)

        # Count assessments
        assessments = Assessment.objects.filter(school=school)
        total_assessments = assessments.count()

        # Count adapted assessments by status
        adapted = AdaptedAssessment.objects.filter(assessment__school=school)
        pending_count = adapted.filter(status='pending').count()
        approved_count = adapted.filter(status='approved').count()

        # Count students
        students = StudentProfile.objects.filter(school=school, is_active=True)
        student_count = students.count()

        # Recent assessments
        recent_assessments = AssessmentListSerializer(
            assessments.order_by('-created_at')[:5],
            many=True
        ).data

        # Pending reviews
        pending_reviews = AdaptedAssessmentListSerializer(
            adapted.filter(status='pending').order_by('-created_at')[:5],
            many=True
        ).data

        return Response({
            'total_assessments': total_assessments,
            'pending_review': pending_count,
            'approved': approved_count,
            'student_count': student_count,
            'recent_assessments': recent_assessments,
            'pending_reviews': pending_reviews
        })


# ============== School Views ==============

class SchoolViewSet(viewsets.ModelViewSet):
    """ViewSet for schools."""
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own school
        if self.request.user.school:
            return School.objects.filter(id=self.request.user.school.id)
        return School.objects.none()

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's school."""
        if request.user.school:
            serializer = self.get_serializer(request.user.school)
            return Response(serializer.data)
        return Response({'error': 'No school associated'}, status=400)


# ============== User Views ==============

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for users."""
    permission_classes = [IsAuthenticated, IsSENCOOrAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        # Users can only see users in their school
        if self.request.user.school:
            return User.objects.filter(school=self.request.user.school)
        return User.objects.none()


# ============== Student Profile Views ==============

class StudentProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for student profiles."""
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentProfileCreateSerializer
        if self.action == 'list':
            return StudentProfileListSerializer
        return StudentProfileSerializer

    def get_queryset(self):
        queryset = StudentProfile.objects.filter(
            school=self.request.user.school
        ).prefetch_related('conditions')

        # Filter by year group
        year_group = self.request.query_params.get('year_group')
        if year_group:
            queryset = queryset.filter(year_group=year_group)

        # Filter by condition
        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(conditions__condition_type=condition)

        # Filter by active status
        active = self.request.query_params.get('active')
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() == 'true')

        return queryset.distinct()

    @action(detail=True, methods=['get', 'put', 'patch'])
    def settings(self, request, pk=None):
        """Get or update adaptation settings for a student."""
        student = self.get_object()
        try:
            settings = student.adaptation_settings
        except AdaptationSettings.DoesNotExist:
            settings = AdaptationSettings.objects.create(student_profile=student)

        if request.method == 'GET':
            serializer = AdaptationSettingsSerializer(settings)
            return Response(serializer.data)

        serializer = AdaptationSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get', 'post'])
    def conditions(self, request, pk=None):
        """Get or add conditions for a student."""
        student = self.get_object()

        if request.method == 'GET':
            conditions = student.conditions.all()
            serializer = StudentConditionSerializer(conditions, many=True)
            return Response(serializer.data)

        serializer = StudentConditionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student_profile=student)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get', 'post'])
    def subject_adaptations(self, request, pk=None):
        """Get or add subject-specific adaptations."""
        student = self.get_object()

        if request.method == 'GET':
            adaptations = student.subject_adaptations.all()
            serializer = SubjectAdaptationSerializer(adaptations, many=True)
            return Response(serializer.data)

        serializer = SubjectAdaptationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student_profile=student)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# ============== Assessment Views ==============

class AssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for assessments."""
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_serializer_class(self):
        if self.action == 'create':
            return AssessmentCreateSerializer
        if self.action == 'list':
            return AssessmentListSerializer
        return AssessmentSerializer

    def get_queryset(self):
        queryset = Assessment.objects.filter(
            school=self.request.user.school
        ).annotate(
            adaptation_count=Count('adapted_versions'),
            pending_review_count=Count('adapted_versions', filter=Q(adapted_versions__status='pending')),
            approved_count=Count('adapted_versions', filter=Q(adapted_versions__status='approved'))
        )

        # Filter by subject
        subject = self.request.query_params.get('subject')
        if subject:
            queryset = queryset.filter(subject=subject)

        # Filter by year group
        year_group = self.request.query_params.get('year_group')
        if year_group:
            queryset = queryset.filter(year_group=year_group)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=True, methods=['get'])
    def adapted_versions(self, request, pk=None):
        """Get all adapted versions of an assessment."""
        assessment = self.get_object()
        adapted = assessment.adapted_versions.all().select_related(
            'student_profile', 'reviewed_by'
        )
        serializer = AdaptedAssessmentListSerializer(adapted, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def extract_text(self, request, pk=None):
        """Trigger text extraction for an assessment."""
        assessment = self.get_object()
        # This would trigger a Celery task in production
        # For now, just update status
        assessment.status = 'processing'
        assessment.save()
        return Response({'message': 'Text extraction started'})


class GenerateAdaptationsView(views.APIView):
    """Generate adaptations for an assessment."""
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def post(self, request, pk):
        try:
            assessment = Assessment.objects.get(
                pk=pk, school=request.user.school
            )
        except Assessment.DoesNotExist:
            return Response(
                {'error': 'Assessment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = GenerateAdaptationsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        created_adaptations = []

        if data.get('student_ids'):
            students = StudentProfile.objects.filter(
                id__in=data['student_ids'],
                school=request.user.school
            )
            for student in students:
                # Create adaptation record (actual generation would be async)
                adapted = AdaptedAssessment.objects.create(
                    assessment=assessment,
                    student_profile=student,
                    adapted_content='',  # Will be filled by AI
                    status='generating'
                )
                created_adaptations.append(adapted)
                # In production: trigger Celery task here

        if data.get('template_id'):
            try:
                template = AdaptationTemplate.objects.get(
                    id=data['template_id']
                )
                adapted = AdaptedAssessment.objects.create(
                    assessment=assessment,
                    adaptation_template=template,
                    adapted_content='',
                    status='generating'
                )
                created_adaptations.append(adapted)
            except AdaptationTemplate.DoesNotExist:
                pass

        return Response({
            'message': f'Generating {len(created_adaptations)} adaptations',
            'adaptation_ids': [str(a.id) for a in created_adaptations]
        }, status=201)


# ============== Adapted Assessment Views ==============

class AdaptedAssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for adapted assessments."""
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_serializer_class(self):
        if self.action == 'list':
            return AdaptedAssessmentListSerializer
        return AdaptedAssessmentSerializer

    def get_queryset(self):
        queryset = AdaptedAssessment.objects.filter(
            assessment__school=self.request.user.school
        ).select_related(
            'assessment', 'student_profile', 'reviewed_by'
        )

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by assessment
        assessment_id = self.request.query_params.get('assessment')
        if assessment_id:
            queryset = queryset.filter(assessment_id=assessment_id)

        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an adapted assessment."""
        adapted = self.get_object()
        adapted.status = 'approved'
        adapted.reviewed_by = request.user
        adapted.reviewed_at = timezone.now()
        adapted.review_notes = request.data.get('review_notes', '')
        adapted.save()
        return Response({'message': 'Approved successfully'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an adapted assessment."""
        adapted = self.get_object()
        adapted.status = 'rejected'
        adapted.reviewed_by = request.user
        adapted.reviewed_at = timezone.now()
        adapted.review_notes = request.data.get('review_notes', '')
        adapted.save()
        return Response({'message': 'Rejected'})

    @action(detail=True, methods=['put', 'patch'])
    def edit(self, request, pk=None):
        """Edit adapted content manually."""
        adapted = self.get_object()
        edited_content = request.data.get('edited_content')
        if edited_content:
            adapted.edited_content = edited_content
            adapted.manually_edited = True
            adapted.status = 'needs_edit'  # Goes back to pending after edit
            adapted.save()
            return Response({'message': 'Content updated'})
        return Response({'error': 'No content provided'}, status=400)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download PDF version."""
        adapted = self.get_object()
        if adapted.output_pdf:
            # Return file URL
            return Response({'url': adapted.output_pdf.url})
        return Response({'error': 'PDF not available'}, status=404)


# ============== Template Views ==============

class AdaptationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for adaptation templates."""
    serializer_class = AdaptationTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return global templates and school-specific templates
        return AdaptationTemplate.objects.filter(
            Q(is_global=True) | Q(school=self.request.user.school)
        )

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            created_by=self.request.user
        )

    @action(detail=False, methods=['get'])
    def global_templates(self, request):
        """Get only global templates."""
        templates = AdaptationTemplate.objects.filter(is_global=True)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


# ============== Reference Data Views ==============

class ConditionTypesView(views.APIView):
    """Get available condition types."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conditions = [
            {
                'value': choice[0],
                'label': choice[1],
                'description': self._get_description(choice[0])
            }
            for choice in StudentCondition.ConditionType.choices
        ]
        return Response(conditions)

    def _get_description(self, condition_type):
        descriptions = {
            'dyslexia': 'Difficulty with reading, spelling, and decoding text',
            'autism': 'Differences in communication, social interaction, and sensory processing',
            'adhd': 'Challenges with attention, focus, and executive function',
            'dyscalculia': 'Difficulty with numbers, calculations, and mathematical concepts',
            'visual_processing': 'Challenges processing visual information',
            'auditory_processing': 'Difficulty processing spoken information',
            'working_memory': 'Limited capacity to hold information while processing',
            'processing_speed': 'Takes longer to process and respond to information',
            'anxiety': 'Excessive worry affecting test performance',
            'eal': 'English is not the primary language'
        }
        return descriptions.get(condition_type, '')


class DefaultSettingsView(views.APIView):
    """Get default adaptation settings for conditions."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        condition = request.query_params.get('condition')
        if condition:
            return Response(self._get_defaults_for_condition(condition))
        return Response(self._get_all_defaults())

    def _get_defaults_for_condition(self, condition):
        """Get recommended default settings for a specific condition."""
        defaults = {
            'dyslexia': {
                'font': 'opendyslexic',
                'font_size': 16,
                'line_spacing': 1.75,
                'letter_spacing': 10,
                'background_colour': 'cream',
                'syllable_breaking': True,
                'key_word_highlighting': True,
                'reading_year_level': 7,
                'max_sentence_length': 12,
                'tts_enabled': True
            },
            'autism': {
                'literal_language_mode': True,
                'literal_language_intensity': 8,
                'explicit_instructions': True,
                'progress_indicators': True,
                'section_breaks': True,
                'timer_display': 'hide',
                'visual_density': 3,
                'feedback_style': 'neutral'
            },
            'adhd': {
                'questions_per_section': 2,
                'progress_indicators': True,
                'key_word_highlighting': True,
                'reference_panels': True,
                'visual_density': 3,
                'section_breaks': True,
                'encouragement_prompts': True
            },
            'dyscalculia': {
                'scaffolded_answers': True,
                'reference_panels': True,
                'numbered_steps': True,
                'visual_density': 3
            },
            'anxiety': {
                'timer_display': 'hide',
                'feedback_style': 'encouraging',
                'encouragement_prompts': True,
                'anxiety_reduction': True,
                'progress_indicators': True
            }
        }
        return defaults.get(condition, {})

    def _get_all_defaults(self):
        """Get base default settings."""
        return {
            'reading_year_level': 8,
            'max_sentence_length': 15,
            'vocabulary_simplification': 5,
            'font': 'arial',
            'font_size': 14,
            'line_spacing': 1.5,
            'background_colour': 'cream',
            'text_colour': 'dark_grey',
            'questions_per_section': 3,
            'numbered_steps': True,
            'progress_indicators': True
        }
