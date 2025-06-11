from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'', AppointmentViewSet, basename='appointment')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]