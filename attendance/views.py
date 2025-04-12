from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Student, AttendanceRecord
from core.models import ClassSession
from .utils import verify_location
import json

def mark_attendance_form(request, session_key):
    """Display form for students to mark attendance"""
    session = get_object_or_404(ClassSession, session_key=session_key, is_active=True)
    
    context = {
        'session': session,
        'course': session.course,
    }
    
    return render(request, 'attendance/mark_form.html', context)

@require_POST
def submit_attendance(request, session_key):
    """Process attendance submission with location verification"""
    try:
        # Get session
        session = get_object_or_404(ClassSession, session_key=session_key, is_active=True)
        
        # Parse JSON data
        data = json.loads(request.body)
        roll_number = data.get('roll_number')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Validate input
        if not roll_number or not latitude or not longitude:
            return JsonResponse({
                'success': False,
                'message': 'Missing required information'
            }, status=400)
        
        # Get or create student
        student, created = Student.objects.get_or_create(
            roll_number=roll_number,
            defaults={'first_name': '', 'last_name': ''}
        )
        
        # Check for existing attendance
        if AttendanceRecord.objects.filter(session=session, student=student).exists():
            return JsonResponse({
                'success': False,
                'message': 'Attendance already marked for this session'
            }, status=400)
        
        # Verify location
        student_location = (float(latitude), float(longitude))
        class_location = (session.latitude, session.longitude)
        verification = verify_location(
            student_location,
            class_location,
            session.allowed_radius
        )
        
        # Create attendance record
        record = AttendanceRecord(
            session=session,
            student=student,
            latitude=latitude,
            longitude=longitude,
            ip_address=request.META.get('REMOTE_ADDR'),
            is_verified=verification['is_within_radius'],
            verification_method="GPS",
            distance_from_class=verification['distance']
        )
        
        # Flag if outside radius
        if not verification['is_within_radius']:
            record.flagged = True
            record.flag_reason = f"Distance {verification['distance']:.1f}m exceeds allowed radius {verification['allowed_radius']}m"
        
        record.save()
        
        return JsonResponse({
            'success': True,
            'verified': verification['is_within_radius'],
            'distance': verification['distance'],
            'message': 'Attendance recorded successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
