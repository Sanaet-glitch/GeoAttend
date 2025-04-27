from django.urls import path
from . import views

app_name = 'faculty'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/create/', views.create_session, name='create_session'),
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/<int:session_id>/edit/', views.edit_session, name='edit_session'),
    path('sessions/<int:session_id>/report/', views.attendance_report, name='attendance_report'),
    path('sessions/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    path('sessions/<int:session_id>/attendance_records_partial/', views.attendance_records_partial, name='attendance_records_partial'),
    path('sessions/<int:session_id>/attendance_count/', views.attendance_count_api, name='attendance_count_api'),
    path('courses/<int:course_id>/enrollments/', views.course_enrollments, name='course_enrollments'),
    path('assignments/<int:assignment_id>/delete/', views.delete_course_assignment, name='delete_course_assignment'),
    path('profile/', views.faculty_profile, name='faculty_profile'),
]
