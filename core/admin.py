from django.contrib import admin
from .models import Course, ClassSession

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'created_at')
    search_fields = ('course_code', 'title')

@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'faculty', 'date', 'start_time', 'end_time', 'is_active')
    list_filter = ('course', 'date', 'is_active')
    search_fields = ('title', 'course__title', 'faculty__username')
