from django.contrib import admin
from .models import Student, AttendanceRecord

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'first_name', 'last_name')
    search_fields = ('roll_number', 'first_name', 'last_name')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'timestamp', 'is_verified', 'flagged')
    list_filter = ('is_verified', 'flagged', 'verification_method')
    search_fields = ('student__roll_number', 'student__first_name', 'student__last_name', 'session__title')
