"""
URL configuration for the core app.
Maps core views to URL patterns for the home page and enrollment key management.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('course/<int:course_id>/enrollment-key/', views.manage_enrollment_key, name='manage_enrollment_key'),
]
