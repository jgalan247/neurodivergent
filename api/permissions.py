"""
Custom permissions for AdaptEd API.
"""
from rest_framework import permissions


class IsSchoolMember(permissions.BasePermission):
    """
    Permission check for school membership.
    Users can only access resources from their own school.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.school is not None

    def has_object_permission(self, request, view, obj):
        # Check if the object belongs to the user's school
        if hasattr(obj, 'school'):
            return obj.school == request.user.school
        if hasattr(obj, 'assessment'):
            return obj.assessment.school == request.user.school
        if hasattr(obj, 'student_profile'):
            return obj.student_profile.school == request.user.school
        return True


class IsSENCOOrAdmin(permissions.BasePermission):
    """
    Permission for SENCO or Admin users only.
    Used for sensitive operations like managing student profiles.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Allow read operations for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write operations require SENCO or Admin role
        return request.user.role in ['senco', 'admin']


class IsTeacherOrAbove(permissions.BasePermission):
    """
    Permission for teachers, SENCOs, and admins.
    Excludes student role.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['teacher', 'senco', 'admin']


class CanReviewAdaptations(permissions.BasePermission):
    """
    Permission for reviewing and approving adaptations.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # All teachers can review
        return request.user.is_teacher

    def has_object_permission(self, request, view, obj):
        # Must be from same school
        if hasattr(obj, 'assessment'):
            return obj.assessment.school == request.user.school
        return True
