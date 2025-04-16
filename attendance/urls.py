from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('mark/<uuid:session_key>/', views.mark_attendance_form, name='mark_attendance_form'),
    path('submit/<uuid:session_key>/', views.submit_attendance, name='submit'),
    path('enroll/', views.enroll_in_course, name='enroll_in_course'),
    path('my-courses/', views.view_enrollments, name='view_enrollments'),
    path('my-attendance/', views.student_attendance, name='student_attendance'),
    path('api/attendance/mark/<uuid:session_key>/', views.api_mark_attendance, name='api_mark_attendance'),
]
