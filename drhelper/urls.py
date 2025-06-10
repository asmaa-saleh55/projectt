from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# ✅ إضافة views الخاصة بـ Simple JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/chatbot/', include('chatbot.urls')),

    # ✅ Endpoints لتسجيل الدخول وتحديث التوكن:
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Serve React App - this should be last to catch all remaining routes
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
