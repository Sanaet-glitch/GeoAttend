"""
Django admin configuration for the attendance app.
Registers Student and AttendanceRecord models and customizes their admin interface.
"""

from django.contrib import admin
from .models import Student, AttendanceRecord

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # Display student details in the admin list view
    list_display = ('admission_number', 'first_name', 'last_name')
    search_fields = ('admission_number', 'first_name', 'last_name')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    # Display and filter attendance records for easy management
    list_display = ('student', 'session', 'timestamp', 'is_verified')
    list_filter = ('is_verified', 'verification_method')
    search_fields = ('student__admission_number', 'student__first_name', 'student__last_name', 'session__title')
