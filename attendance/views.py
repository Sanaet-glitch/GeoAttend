from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import Student, AttendanceRecord
from core.models import ClassSession, Course, Enrollment, EnrollmentKey

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
        
        # Check if session has ended
        if session.get_status() == "Ended":
            return JsonResponse({
                'success': False,
                'message': 'Attendance marking is not allowed. The session has already ended.'
            }, status=400)
        
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
        
        # Check if student is enrolled in the course and approved
        if not Enrollment.objects.filter(student=student, course=session.course, status='approved').exists():
            return JsonResponse({
                'success': False,
                'message': 'You are not approved to attend this course. Please ensure your enrollment is approved.'
            }, status=403)
        
        # Check for existing attendance by student for this session
        if AttendanceRecord.objects.filter(session=session, student=student).exists():
            return JsonResponse({
                'success': False,
                'message': 'Attendance already marked for this session for this admission number.'
            }, status=400)
        
        # Create attendance record
        record = AttendanceRecord(
            session=session,
            student=student
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

def api_mark_attendance(request, session_key):
    """API endpoint for attendance marking (GET only for now)"""
    if request.method == 'GET':
        return JsonResponse({'detail': 'API endpoint is reachable. Use POST to submit attendance.'})
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)

def enroll_in_course(request):
    """Allow students to enroll in courses using an enrollment key"""
    if request.method == 'POST':
        admission_number = request.POST.get('admission_number')
        enrollment_key = request.POST.get('enrollment_key')
        
        if not admission_number or not enrollment_key:
            messages.error(request, 'Please provide both admission number and enrollment key.')
            return redirect('attendance:enroll_in_course')
        
        # Get student
        student = get_object_or_404(Student, admission_number=admission_number)
        
        # Verify enrollment key
        try:
            key_obj = EnrollmentKey.objects.get(key=enrollment_key)
            course = key_obj.course
            # Check for expiry
            if key_obj.expires_at and timezone.now() > key_obj.expires_at:
                messages.error(request, 'This enrollment key has expired. Please contact your lecturer for a new key.')
                return redirect('attendance:enroll_in_course')
        except EnrollmentKey.DoesNotExist:
            messages.error(request, 'Invalid enrollment key. Please check and try again.')
            return redirect('attendance:enroll_in_course')
        
        # Check if already enrolled
        existing = Enrollment.objects.filter(student=student, course=course).first()
        if existing:
            if existing.status == 'pending':
                messages.info(request, f'Your enrollment in {course.course_code}: {course.title} is pending approval.')
            elif existing.status == 'approved':
                messages.info(request, f'You are already enrolled in {course.course_code}: {course.title}.')
            elif existing.status == 'rejected':
                messages.warning(request, f'Your enrollment in {course.course_code}: {course.title} was rejected. Please contact your lecturer.')
        else:
            # Create enrollment as pending
            Enrollment.objects.create(
                student=student,
                course=course,
                status='pending'
            )
            messages.success(request, f'Enrollment request submitted for {course.course_code}: {course.title}. Please wait for faculty approval.')
        
        return redirect('attendance:enroll_in_course')
    
    return render(request, 'attendance/enroll_in_course.html')

def view_enrollments(request):
    """Allow students to view which courses they are enrolled in"""
    enrollments = None
    student = None
    
    if request.method == 'POST':
        admission_number = request.POST.get('admission_number')
        
        if not admission_number:
            messages.error(request, 'Please provide your admission number.')
            return redirect('attendance:view_enrollments')
        
        try:
            student = Student.objects.get(admission_number=admission_number)
            enrollments = Enrollment.objects.filter(student=student, status='approved').select_related('course')
        except Student.DoesNotExist:
            messages.error(request, 'Student with this admission number does not exist.')
            return redirect('attendance:view_enrollments')
    
    return render(request, 'attendance/view_enrollments.html', {
        'enrollments': enrollments,
        'student': student
    })

def student_attendance(request):
    """Allow students to view their attendance records for enrolled courses"""
    attendance_records = None
    student = None
    filter_course = None
    
    # Check if there's a course_id in the URL parameters
    course_id = request.GET.get('course_id')
    
    if request.method == 'POST':
        admission_number = request.POST.get('admission_number')
        
        if not admission_number:
            messages.error(request, 'Please provide your admission number.')
            return redirect('attendance:student_attendance')
        
        try:
            student = Student.objects.get(admission_number=admission_number)
            
            # Get all enrollments for this student
            enrollments = Enrollment.objects.filter(student=student).select_related('course')
            
            # Get all attendance records for this student, organized by course
            attendance_records = {}
            for enrollment in enrollments:
                course_records = AttendanceRecord.objects.filter(
                    student=student,
                    session__course=enrollment.course
                ).select_related('session')
                
                attendance_records[enrollment.course] = course_records
                
        except Student.DoesNotExist:
            messages.error(request, 'Student with this admission number does not exist.')
            return redirect('attendance:student_attendance')
    
    # If a GET request includes course_id and admission_number
    elif course_id and request.GET.get('admission_number'):
        admission_number = request.GET.get('admission_number')
        
        try:
            student = Student.objects.get(admission_number=admission_number)
            course = Course.objects.get(id=course_id)
            filter_course = course
            
            # Only get attendance for the specified course
            attendance_records = {
                course: AttendanceRecord.objects.filter(
                    student=student, 
                    session__course=course
                ).select_related('session')
            }
        except (Student.DoesNotExist, Course.DoesNotExist):
            messages.error(request, 'Invalid student or course.')
            return redirect('attendance:student_attendance')
    
    # For a direct link with just course_id
    elif course_id:
        # Store the course_id for later use after the student enters their admission number
        filter_course = get_object_or_404(Course, id=course_id)
    
    return render(request, 'attendance/student_attendance.html', {
        'attendance_records': attendance_records,
        'student': student,
        'filter_course': filter_course
    })
