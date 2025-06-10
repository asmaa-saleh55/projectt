from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LogoutView, ChatbotAskView, AdminStatsView, DoctorPerformanceView,
    AppointmentViewSet, ReviewViewSet, MessageViewSet, DoctorViewSet, UserViewSet, PatientViewSet, register_user, get_user_profile
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('register', register_user, name='register'),
    path('me/', get_user_profile, name='user-profile'),
    path('users/me/', get_user_profile, name='user-profile-alias'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('chatbot/ask/', ChatbotAskView.as_view(), name='chatbot-ask'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('doctor/performance/', DoctorPerformanceView.as_view(), name='doctor-performance'),
    path('', include(router.urls)),
]