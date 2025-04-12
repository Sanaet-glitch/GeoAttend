from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, Q
from django.contrib import messages

from core.models import Course, ClassSession
from attendance.models import AttendanceRecord
from .models import FacultyProfile, CourseAssignment

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
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        allowed_radius = request.POST.get('allowed_radius')
        
        # Validate the form
        if not all([course_id, title, date, start_time, end_time, latitude, longitude, allowed_radius]):
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
            end_time=end_time,
            latitude=float(latitude),
            longitude=float(longitude),
            allowed_radius=int(allowed_radius)
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
        'qr_code': session.get_qr_code(),
        'attendance_count': attendance_records.count(),
        'flagged_count': attendance_records.filter(flagged=True).count(),
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
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        allowed_radius = request.POST.get('allowed_radius')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate the form
        if not all([title, date, start_time, end_time, latitude, longitude, allowed_radius]):
            messages.error(request, 'Please fill in all required fields')
            return redirect('faculty:edit_session', session_id=session_id)
        
        # Update session
        session.title = title
        session.date = date
        session.start_time = start_time
        session.end_time = end_time
        session.latitude = float(latitude)
        session.longitude = float(longitude)
        session.allowed_radius = int(allowed_radius)
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
    
    context = {
        'session': session,
        'attendance_records': attendance_records,
        'attendance_count': attendance_records.count(),
        'verified_count': attendance_records.filter(is_verified=True).count(),
        'flagged_count': attendance_records.filter(flagged=True).count(),
    }
    
    return render(request, 'faculty/attendance_report.html', context)
