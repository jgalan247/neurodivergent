"""
AI Adaptation Engine for AdaptEd.

This module contains the core logic for generating adapted content using AI.
"""
import time
import logging
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class AdaptationEngine:
    """
    Engine for generating adapted assessment content using AI.

    Supports both OpenAI and Azure OpenAI backends.
    """

    def __init__(self):
        self.use_azure = settings.USE_AZURE_OPENAI

        if self.use_azure:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.model = settings.AZURE_OPENAI_DEPLOYMENT
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4o"

    def generate_adaptation(
        self,
        original_content: str,
        student_profile,
        assessment,
        subject_terms: list = None
    ) -> dict:
        """
        Generate adapted content for a student.

        Args:
            original_content: The original assessment text
            student_profile: StudentProfile model instance
            assessment: Assessment model instance
            subject_terms: List of protected subject terms

        Returns:
            dict with 'content', 'tokens_used', 'time_seconds', 'model'
        """
        from .prompt_generator import PromptGenerator

        # Generate the full prompt
        generator = PromptGenerator()
        system_prompt = generator.generate_system_prompt(
            student_profile=student_profile,
            assessment=assessment,
            subject_terms=subject_terms or []
        )

        # Make the API call
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please adapt the following assessment content:\n\n{original_content}"}
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=4096
            )

            adapted_content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            elapsed_time = time.time() - start_time

            logger.info(
                f"Generated adaptation for student {student_profile.id} "
                f"in {elapsed_time:.2f}s using {tokens_used} tokens"
            )

            return {
                'content': adapted_content,
                'tokens_used': tokens_used,
                'time_seconds': elapsed_time,
                'model': self.model,
                'prompt': system_prompt  # For debugging/auditing
            }

        except Exception as e:
            logger.error(f"Error generating adaptation: {str(e)}")
            raise


class AdaptationValidator:
    """
    Validates adapted content to ensure quality and accuracy.
    """

    def validate(self, original: str, adapted: str, assessment, student_profile) -> dict:
        """
        Validate adapted content.

        Returns:
            dict with 'valid', 'errors', 'warnings'
        """
        errors = []
        warnings = []

        # 1. Check for potential answered questions
        if self._might_contain_answers(original, adapted):
            warnings.append("AI may have provided answers - please verify")

        # 2. Check protected terms are preserved
        protected_terms = assessment.protected_terms or []
        for term in protected_terms:
            if term.lower() in original.lower() and term.lower() not in adapted.lower():
                warnings.append(f"Protected term '{term}' may have been modified")

        # 3. Check question count
        original_q = self._count_questions(original)
        adapted_q = self._count_questions(adapted)
        if original_q != adapted_q:
            warnings.append(
                f"Question count changed: {original_q} → {adapted_q}"
            )

        # 4. Check length ratio
        if len(original) > 0:
            ratio = len(adapted) / len(original)
            if ratio > 3:
                warnings.append("Adapted version is significantly longer than original")
            elif ratio < 0.5:
                warnings.append("Adapted version is significantly shorter than original")

        # 5. Check for mathematical notation if flagged
        content_flags = assessment.content_flags or {}
        if content_flags.get('mathematical_notation'):
            if not self._maths_preserved(original, adapted):
                warnings.append("Mathematical notation may have been altered")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _might_contain_answers(self, original: str, adapted: str) -> bool:
        """Check if adapted content might contain answers to questions."""
        # Look for patterns that suggest answers were added
        answer_indicators = [
            'the answer is',
            'therefore,',
            '= ',
            'solution:',
            'answer:',
        ]
        adapted_lower = adapted.lower()
        original_lower = original.lower()

        for indicator in answer_indicators:
            if indicator in adapted_lower and indicator not in original_lower:
                return True
        return False

    def _count_questions(self, text: str) -> int:
        """Count questions in text."""
        import re
        # Count numbered questions
        numbered = len(re.findall(r'(?:^|\n)\s*(?:Q(?:uestion)?\.?\s*)?\d+[.):]\s', text))
        # Count question marks
        questions = text.count('?')
        return max(numbered, questions // 2)  # Rough estimate

    def _maths_preserved(self, original: str, adapted: str) -> bool:
        """Check if mathematical notation is preserved."""
        import re
        # Extract mathematical expressions
        math_patterns = [
            r'\d+\s*[+\-×÷/]\s*\d+',  # Basic operations
            r'\d+/\d+',  # Fractions
            r'\d+\s*=\s*\d+',  # Equations
            r'[a-z]\s*=',  # Variables
        ]

        for pattern in math_patterns:
            original_matches = set(re.findall(pattern, original))
            adapted_matches = set(re.findall(pattern, adapted))
            # Check if all original math expressions are in adapted
            if not original_matches.issubset(adapted_matches):
                return False
        return True


def process_adaptation(adapted_assessment_id: str):
    """
    Process an adaptation asynchronously.

    This function would typically be called from a Celery task.
    """
    from assessments.models import AdaptedAssessment
    from adaptations.models import SubjectTerms

    try:
        adapted = AdaptedAssessment.objects.get(id=adapted_assessment_id)
    except AdaptedAssessment.DoesNotExist:
        logger.error(f"AdaptedAssessment {adapted_assessment_id} not found")
        return

    assessment = adapted.assessment
    student_profile = adapted.student_profile

    # Get subject terms
    subject_terms = []
    try:
        terms = SubjectTerms.objects.get(subject=assessment.subject)
        subject_terms = terms.terms
    except SubjectTerms.DoesNotExist:
        pass

    # Add assessment-specific protected terms
    subject_terms.extend(assessment.protected_terms or [])

    try:
        # Generate adaptation
        engine = AdaptationEngine()
        result = engine.generate_adaptation(
            original_content=assessment.extracted_text,
            student_profile=student_profile,
            assessment=assessment,
            subject_terms=subject_terms
        )

        # Update the adapted assessment
        adapted.adapted_content = result['content']
        adapted.ai_model = result['model']
        adapted.ai_tokens_used = result['tokens_used']
        adapted.adaptation_time_seconds = result['time_seconds']
        adapted.adaptation_prompt = result['prompt']

        # Validate
        validator = AdaptationValidator()
        validation = validator.validate(
            original=assessment.extracted_text,
            adapted=result['content'],
            assessment=assessment,
            student_profile=student_profile
        )

        adapted.validation_results = validation
        adapted.validation_warnings = validation['warnings']
        adapted.status = 'pending'  # Ready for review
        adapted.save()

        logger.info(f"Successfully processed adaptation {adapted_assessment_id}")

    except Exception as e:
        logger.error(f"Error processing adaptation {adapted_assessment_id}: {str(e)}")
        adapted.status = 'error'
        adapted.save()
        raise
