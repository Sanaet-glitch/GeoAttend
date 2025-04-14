from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Student, AttendanceRecord
from core.models import ClassSession
import json

def mark_attendance_form(request, session_key):
    """Display form for students to mark attendance"""
    session = get_object_or_404(ClassSession, session_key=session_key, is_active=True)
    
    context = {
        'session': session,
        'course': session.course,
    }
    
    return render(request, 'attendance/mark_form.html', context)

@csrf_exempt
@require_POST
def submit_attendance(request, session_key):
    """Process attendance submission"""
    try:
        # Get session
        session = get_object_or_404(ClassSession, session_key=session_key, is_active=True)
        
        # Parse JSON data
        data = json.loads(request.body)
        admission_number = data.get('admission_number')
        
        # Debugging logs
        print(f"Received session_key: {session_key}")
        print(f"Received admission_number: {admission_number}")

        # Validate input
        if not admission_number:
            return JsonResponse({
                'success': False,
                'message': 'Missing required information'
            }, status=400)
        
        # Get or create student
        student, created = Student.objects.get_or_create(
            admission_number=admission_number,
            defaults={'first_name': '', 'last_name': ''}
        )
        
        # Check for existing attendance by student or IP for this session
        ip_address = request.META.get('REMOTE_ADDR')
        if AttendanceRecord.objects.filter(session=session, student=student).exists() or \
           AttendanceRecord.objects.filter(session=session, ip_address=ip_address).exists():
            return JsonResponse({
                'success': False,
                'message': 'Attendance already marked for this session from this device or admission number.'
            }, status=400)
        
        # Create attendance record with ip_address
        record = AttendanceRecord(
            session=session,
            student=student,
            ip_address=ip_address
        )
        record.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Attendance recorded successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
