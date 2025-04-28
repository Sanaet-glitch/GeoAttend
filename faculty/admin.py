"""
Django admin configuration for the faculty app.
Registers faculty-related models and customizes their admin interface.
"""

from django.contrib import admin
from .models import FacultyProfile, CourseAssignment

@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')

@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'course', 'semester', 'year')
    list_filter = ('semester', 'year')
    search_fields = ('faculty__user__username', 'course__title', 'course__course_code')
