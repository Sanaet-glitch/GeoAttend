from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.db.models import Count, Q
from django.contrib import messages
from django.utils.timezone import now
import csv

from core.models import Course, ClassSession, Enrollment, EnrollmentKey
from attendance.models import AttendanceRecord, Student
from .models import FacultyProfile, CourseAssignment
from administration.views import log_admin_action

# Helper function to check if user is admin
from django.contrib.auth.models import User

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
def dashboard(request):
    """Faculty dashboard showing courses and recent sessions"""
    # Get or create faculty profile
    faculty_profile, created = FacultyProfile.objects.get_or_create(
        user=request.user,
        defaults={'department': 'General'}
    )
    
    # Get assigned courses
    course_assignments = CourseAssignment.objects.filter(faculty=faculty_profile)
    courses = [assignment.course for assignment in course_assignments]
    
    # Get recent sessions
    recent_sessions = ClassSession.objects.filter(
        course__in=courses,
        faculty=request.user,
        date__gte=timezone.now().date() - timezone.timedelta(days=7)
    ).order_by('-date', '-start_time')[:5]
    
    # Count attendance for each session
    for session in recent_sessions:
        session.attendance_count = AttendanceRecord.objects.filter(session=session).count()
    
    context = {
        'faculty': faculty_profile,
        'courses': courses,
        'recent_sessions': recent_sessions,
    }
    
    return render(request, 'faculty/dashboard.html', context)

@login_required
def session_list(request):
    """List all sessions for the faculty member"""
    # Get or create faculty profile
    faculty_profile, created = FacultyProfile.objects.get_or_create(
        user=request.user,
        defaults={'department': 'General'}
    )
    
    # Get assigned courses
    course_assignments = CourseAssignment.objects.filter(faculty=faculty_profile)
    courses = [assignment.course for assignment in course_assignments]
    
    # Improved: Automatically deactivate sessions whose end datetime has passed
    from datetime import datetime
    from django.utils.timezone import make_aware, is_naive
    now_dt = timezone.localtime(timezone.now())
    expired_sessions = ClassSession.objects.filter(is_active=True)
    for session in expired_sessions:
        session_end = datetime.combine(session.date, session.end_time)
        if is_naive(session_end):
            session_end = make_aware(session_end)
        session_end = timezone.localtime(session_end)
        if now_dt > session_end:
            session.is_active = False
            session.save()
    
    # Filter sessions
    filter_course = request.GET.get('course')
    filter_date_start = request.GET.get('date_start')
    filter_date_end = request.GET.get('date_end')
    
    sessions = ClassSession.objects.filter(
        course__in=courses,
        faculty=request.user
    )
    
    # Apply filters if provided
    if filter_course:
        sessions = sessions.filter(course__course_code=filter_course)
        
    if filter_date_start:
        sessions = sessions.filter(date__gte=filter_date_start)
        
    if filter_date_end:
        sessions = sessions.filter(date__lte=filter_date_end)
    
    # Order by date and time
    sessions = sessions.order_by('-date', '-start_time')
    
    # Count attendance for each session
    for session in sessions:
        session.attendance_count = AttendanceRecord.objects.filter(session=session).count()
    
    context = {
        'faculty': faculty_profile,
        'courses': courses,
        'sessions': sessions,
        'filter_course': filter_course,
        'filter_date_start': filter_date_start,
        'filter_date_end': filter_date_end,
    }
    
    return render(request, 'faculty/session_list.html', context)

@login_required
def create_session(request):
    """Create a new class session"""
    # Get or create faculty profile
    faculty_profile, created = FacultyProfile.objects.get_or_create(
        user=request.user,
        defaults={'department': 'General'}
    )
    
    # Get assigned courses
    course_assignments = CourseAssignment.objects.filter(faculty=faculty_profile)
    courses = [assignment.course for assignment in course_assignments]
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        title = request.POST.get('title')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        if not all([course_id, title, date, start_time, end_time]):
            messages.error(request, 'Please fill in all required fields')
            return redirect('faculty:create_session')
            
        # Check if course is assigned to faculty
        course = get_object_or_404(Course, id=course_id)
        if course not in courses:
            return HttpResponseForbidden("You don't have permission to create sessions for this course")
        
        # Create session
        session = ClassSession.objects.create(
            course=course,
            faculty=request.user,
            title=title,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        
        messages.success(request, f'Session "{title}" created successfully')
        return redirect('faculty:session_detail', session_id=session.id)
    
    context = {
        'faculty': faculty_profile,
        'courses': courses,
    }
    
    return render(request, 'faculty/create_session.html', context)

@login_required
def session_detail(request, session_id):
    """View details of a specific session, including attendance records"""
    # Get or create faculty profile
    faculty_profile, created = FacultyProfile.objects.get_or_create(
        user=request.user,
        defaults={'department': 'General'}
    )
    
    # Get session
    session = get_object_or_404(ClassSession, id=session_id)
    
    # Check if faculty owns the session
    if session.faculty != request.user:
        return HttpResponseForbidden("You don't have permission to view this session")
    
    # Get attendance records
    attendance_records = AttendanceRecord.objects.filter(session=session)
    
    context = {
        'faculty': faculty_profile,
        'session': session,
        'attendance_records': attendance_records,
        'qr_code': session.get_qr_code(request),
        'attendance_count': attendance_records.count(),
    }
    
    return render(request, 'faculty/session_detail.html', context)

@login_required
def edit_session(request, session_id):
    """Edit an existing class session"""
    # Get or create faculty profile
    faculty_profile, created = FacultyProfile.objects.get_or_create(
        user=request.user,
        defaults={'department': 'General'}
    )
    
    # Get session
    session = get_object_or_404(ClassSession, id=session_id)
    
    # Check if faculty owns the session
    if session.faculty != request.user:
        return HttpResponseForbidden("You don't have permission to edit this session")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate the form
        if not all([title, date, start_time, end_time]):
            messages.error(request, 'Please fill in all required fields')
            return redirect('faculty:edit_session', session_id=session_id)
        
        # Update session
        session.title = title
        session.date = date
        session.start_time = start_time
        session.end_time = end_time
        session.is_active = is_active
        session.save()
        
        messages.success(request, f'Session "{title}" updated successfully')
        return redirect('faculty:session_detail', session_id=session.id)
    
    context = {
        'faculty': faculty_profile,
        'session': session,
    }
    
    return render(request, 'faculty/edit_session.html', context)

@login_required
def attendance_report(request, session_id):
    """Generate attendance report for a session"""
    # Get session
    session = get_object_or_404(ClassSession, id=session_id)
    
    # Check if faculty owns the session
    if session.faculty != request.user:
        return HttpResponseForbidden("You don't have permission to access this report")
    
    # Get attendance records
    attendance_records = AttendanceRecord.objects.filter(session=session)
    
    # Add session details as a heading in the CSV file
    csv_data = [
        [
            f"Course: {session.course.course_code} - {session.course.title}",
            f"Date: {session.date}",
            f"Time: {session.start_time} - {session.end_time}",
            f"Lecturer: {session.faculty.get_full_name()}",
            f"Semester: {session.semester}"
        ],
        []  # Empty row for spacing
    ]

    # Add column headers
    csv_data.append(["Admission Number", "Name", "Timestamp", "Status"])

    # Add attendance records
    for record in attendance_records:
        csv_data.append([
            record.student.admission_number,
            f"{record.student.first_name} {record.student.last_name}",
            record.timestamp.strftime("%B %d, %Y %H:%M"),
            "Verified" if record.is_verified else "Not Verified"
        ])

    # Generate CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{session.id}.csv"'

    writer = csv.writer(response)
    writer.writerows(csv_data)

    return response

@login_required
def delete_session(request, session_id):
    """Delete a specific class session"""
    session = get_object_or_404(ClassSession, id=session_id, faculty=request.user)
    session.delete()
    messages.success(request, 'Session deleted successfully.')
    return redirect('faculty:session_list')

@login_required
def course_enrollments(request, course_id):
    """View students enrolled in a specific course and approve/reject pending enrollments"""
    course = get_object_or_404(Course, id=course_id, lecturers=request.user)
    
    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        action = request.POST.get('action')
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, course=course)
        if action == 'approve':
            enrollment.status = 'approved'
            enrollment.save()
            messages.success(request, f"Enrollment for {enrollment.student.admission_number} approved.")
        elif action == 'reject':
            enrollment.status = 'rejected'
            enrollment.save()
            messages.warning(request, f"Enrollment for {enrollment.student.admission_number} rejected.")
        return redirect('faculty:course_enrollments', course_id=course.id)
    
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    pending_enrollments = enrollments.filter(status='pending')
    approved_enrollments = enrollments.filter(status='approved')
    rejected_enrollments = enrollments.filter(status='rejected')
    
    try:
        enrollment_key = EnrollmentKey.objects.get(course=course)
    except EnrollmentKey.DoesNotExist:
        enrollment_key = None
    
    context = {
        'course': course,
        'enrollments': enrollments,
        'pending_enrollments': pending_enrollments,
        'approved_enrollments': approved_enrollments,
        'rejected_enrollments': rejected_enrollments,
        'enrollment_key': enrollment_key,
    }
    
    return render(request, 'faculty/course_enrollments.html', context)

@login_required
@user_passes_test(is_admin)
def delete_course_assignment(request, assignment_id):
    """Delete a specific course assignment for a faculty member."""
    assignment = get_object_or_404(CourseAssignment, id=assignment_id)
    assignment.delete()

    # Log action
    log_admin_action(
        request,
        'DELETE',
        'CourseAssignment',
        assignment_id,
        f'Deleted course assignment for {assignment.course.course_code} assigned to {assignment.faculty.user.username}'
    )

    messages.success(request, f'Course assignment for {assignment.course.course_code} deleted successfully.')
    return redirect('administration:faculty_detail', faculty_id=assignment.faculty.id)

@login_required
def attendance_records_partial(request, session_id):
    """Return the attendance records table as an HTML fragment for AJAX refresh."""
    session = get_object_or_404(ClassSession, id=session_id)
    if session.faculty != request.user:
        return HttpResponseForbidden("You don't have permission to view this session")
    attendance_records = AttendanceRecord.objects.filter(session=session)
    return render(request, 'faculty/attendance_records_partial.html', {
        'attendance_records': attendance_records
    })
