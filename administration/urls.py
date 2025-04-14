from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('faculty/', views.faculty_list, name='faculty_list'),
    path('faculty/create/', views.create_faculty, name='create_faculty'),
    path('faculty/<int:faculty_id>/', views.faculty_detail, name='faculty_detail'),
    path('faculty/<int:faculty_id>/assign-course/', views.assign_course, name='assign_course'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('sessions/', views.session_list, name='session_list'),  # New URL
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),  # New URL
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.create_student, name='create_student'),
    path('students/import/', views.import_students, name='import_students'),
    path('students/export/', views.export_students, name='export_students'),
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/create/', views.create_setting, name='create_setting'),
    path('logs/', views.activity_logs, name='activity_logs'),
]
