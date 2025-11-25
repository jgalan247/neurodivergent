"""
API URL configuration for AdaptEd.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'schools', views.SchoolViewSet, basename='school')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'students', views.StudentProfileViewSet, basename='student')
router.register(r'assessments', views.AssessmentViewSet, basename='assessment')
router.register(r'adapted', views.AdaptedAssessmentViewSet, basename='adapted-assessment')
router.register(r'templates', views.AdaptationTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),

    # Authentication endpoints
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/user/', views.CurrentUserView.as_view(), name='current-user'),

    # Dashboard stats
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),

    # Adaptation generation
    path('assessments/<uuid:pk>/generate/', views.GenerateAdaptationsView.as_view(), name='generate-adaptations'),

    # Condition types and settings
    path('conditions/', views.ConditionTypesView.as_view(), name='condition-types'),
    path('settings/defaults/', views.DefaultSettingsView.as_view(), name='default-settings'),
]
