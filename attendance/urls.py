from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('mark/<uuid:session_key>/', views.mark_attendance_form, name='mark_form'),
    path('submit/<uuid:session_key>/', views.submit_attendance, name='submit'),
]
