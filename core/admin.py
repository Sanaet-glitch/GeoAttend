from django.contrib import admin
from .models import Course, ClassSession, EnrollmentKey, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'created_at')
    search_fields = ('course_code', 'title')

@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'faculty', 'date', 'start_time', 'end_time', 'is_active')
    list_filter = ('course', 'date', 'is_active')
    search_fields = ('title', 'course__title', 'faculty__username')

@admin.register(EnrollmentKey)
class EnrollmentKeyAdmin(admin.ModelAdmin):
    list_display = ("course", "key", "expires_at", "regenerated_at", "created_at", "updated_at")
    search_fields = ("course__course_code", "key")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at", "status")
    list_filter = ("status", "course")
    search_fields = ("student__admission_number", "course__course_code")
