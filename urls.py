"""
URL Configuration for GeoAttend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from core.views import redirect_logged_in_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', lambda request: redirect_logged_in_user(request) or LoginView.as_view(template_name='core/login.html')(request), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/attendance/', include('attendance.urls')),
    path('faculty/', include('faculty.urls')), 
    path('administration/', include('administration.urls')), # Include URLs for the administration app
    path('attendance/', include('attendance.urls')), # Include URLs for the attendance app
    path('', include('core.urls')), # Map root URL back to core app's index view
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
