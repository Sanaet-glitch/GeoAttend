from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import csv
import io

from .models import SystemSettings, AdminLog, StudentImportLog
from core.models import Course, ClassSession
from attendance.models import Student, AttendanceRecord
from faculty.models import FacultyProfile, CourseAssignment

# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff or user.is_superuser

# Log admin actions
def log_admin_action(request, action, object_type, object_id=None, details=None):
    AdminLog.objects.create(
        admin=request.user,
        action=action,
        object_type=object_type,
        object_id=str(object_id) if object_id else None,
        details=details,
    )

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard with system overview"""
    # Count records
    student_count = Student.objects.count()
    course_count = Course.objects.count()
    faculty_count = FacultyProfile.objects.count()
    session_count = ClassSession.objects.count()
    attendance_count = AttendanceRecord.objects.count()
    
    # Recent activity
    recent_sessions = ClassSession.objects.order_by('-created_at')[:5]
    recent_attendance = AttendanceRecord.objects.order_by('-timestamp')[:10]
    recent_logs = AdminLog.objects.order_by('-timestamp')[:10]
    
    # Fetch attendance records with optional filters
    filter_course = request.GET.get('course')
    filter_faculty = request.GET.get('faculty')
    filter_date_start = request.GET.get('date_start')
    filter_date_end = request.GET.get('date_end')

    attendance_records = AttendanceRecord.objects.select_related('student', 'session')

    if filter_course:
        attendance_records = attendance_records.filter(session__course__course_code=filter_course)

    if filter_faculty:
        attendance_records = attendance_records.filter(session__faculty__username=filter_faculty)

    if filter_date_start:
        attendance_records = attendance_records.filter(timestamp__date__gte=filter_date_start)

    if filter_date_end:
        attendance_records = attendance_records.filter(timestamp__date__lte=filter_date_end)

    # Fetch unique courses and faculty for filter options
    courses = Course.objects.all()
    faculty_users = User.objects.filter(sessions__isnull=False).distinct()

    # Add attendance records and filter options to context
    context = {
        'student_count': student_count,
        'course_count': course_count,
        'faculty_count': faculty_count,
        'session_count': session_count,
        'attendance_count': attendance_count,
        'recent_sessions': recent_sessions,
        'recent_attendance': recent_attendance,
        'recent_logs': recent_logs,
        'attendance_records': attendance_records,
        'courses': courses,
        'faculty_users': faculty_users,
    }
    
    return render(request, 'administration/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def faculty_list(request):
    """Manage faculty users"""
    faculties = FacultyProfile.objects.all().select_related('user')
    
    # Calculate course assignments for each faculty
    for faculty in faculties:
        faculty.course_count = CourseAssignment.objects.filter(faculty=faculty).count()
    
    context = {
        'faculties': faculties,
    }
    
    return render(request, 'administration/faculty_list.html', context)

@login_required
@user_passes_test(is_admin)
def faculty_detail(request, faculty_id):
    """View and edit faculty details"""
    faculty = get_object_or_404(FacultyProfile, id=faculty_id)
    course_assignments = CourseAssignment.objects.filter(faculty=faculty)
    
    # Get available courses that aren't already assigned
    assigned_courses = [assignment.course for assignment in course_assignments]
    available_courses = Course.objects.exclude(id__in=[course.id for course in assigned_courses])
    
    context = {
        'faculty': faculty,
        'course_assignments': course_assignments,
        'available_courses': available_courses,
    }
    
    return render(request, 'administration/faculty_detail.html', context)

@login_required
@user_passes_test(is_admin)
def create_faculty(request):
    """Create a new faculty account"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        department = request.POST.get('department')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username {username} is already taken.')
            return redirect('administration:create_faculty')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create faculty profile
        faculty = FacultyProfile.objects.create(
            user=user,
            department=department
        )
        
        # Log action
        log_admin_action(
            request, 
            'CREATE', 
            'FacultyProfile', 
            faculty.id, 
            f'Created faculty account for {username}'
        )
        
        messages.success(request, f'Faculty account for {username} created successfully.')
        return redirect('administration:faculty_list')
    
    return render(request, 'administration/create_faculty.html')

@login_required
@user_passes_test(is_admin)
def assign_course(request, faculty_id):
    """Assign a course to a faculty member"""
    faculty = get_object_or_404(FacultyProfile, id=faculty_id)
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        semester = request.POST.get('semester')
        year = request.POST.get('year')
        
        # Get course
        course = get_object_or_404(Course, id=course_id)
        
        # Check if assignment already exists
        if CourseAssignment.objects.filter(faculty=faculty, course=course, semester=semester, year=year).exists():
            messages.error(request, f'This course is already assigned to this faculty for {semester} {year}.')
            return redirect('administration:faculty_detail', faculty_id=faculty.id)
        
        # Create assignment
        assignment = CourseAssignment.objects.create(
            faculty=faculty,
            course=course,
            semester=semester,
            year=year
        )
        
        # Log action
        log_admin_action(
            request, 
            'CREATE', 
            'CourseAssignment', 
            assignment.id, 
            f'Assigned {course.course_code} to {faculty.user.username}'
        )
        
        messages.success(request, f'{course.title} has been assigned to {faculty.user.get_full_name() or faculty.user.username}.')
        
    return redirect('administration:faculty_detail', faculty_id=faculty.id)

@login_required
@user_passes_test(is_admin)
def course_list(request):
    """Manage courses"""
    courses = Course.objects.all()
    
    # Calculate statistics for each course
    for course in courses:
        course.session_count = ClassSession.objects.filter(course=course).count()
        course.faculty_count = CourseAssignment.objects.filter(course=course).count()
    
    context = {
        'courses': courses,
    }
    
    return render(request, 'administration/course_list.html', context)

@login_required
@user_passes_test(is_admin)
def create_course(request):
    """Create a new course"""
    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        # Check if course code already exists
        if Course.objects.filter(course_code=course_code).exists():
            messages.error(request, f'Course code {course_code} is already taken.')
            return redirect('administration:create_course')
        
        # Create course
        course = Course.objects.create(
            course_code=course_code,
            title=title,
            description=description
        )
        
        # Log action
        log_admin_action(
            request, 
            'CREATE', 
            'Course', 
            course.id, 
            f'Created course {course_code}: {title}'
        )
        
        messages.success(request, f'Course {course_code}: {title} created successfully.')
        return redirect('administration:course_list')
    
    return render(request, 'administration/create_course.html')

@login_required
@user_passes_test(is_admin)
def student_list(request):
    """Manage students"""
    students = Student.objects.all()
    
    # Count attendance records for each student
    for student in students:
        student.attendance_count = AttendanceRecord.objects.filter(student=student).count()
    
    context = {
        'students': students,
    }
    
    return render(request, 'administration/student_list.html', context)

@login_required
@user_passes_test(is_admin)
def create_student(request):
    """Create a new student individually from the admin dashboard"""
    if request.method == 'POST':
        admission_number = request.POST.get('admission_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if not all([admission_number, first_name, last_name]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('administration:create_student')
        if Student.objects.filter(admission_number=admission_number).exists():
            messages.error(request, f'Admission number {admission_number} already exists.')
            return redirect('administration:create_student')
        Student.objects.create(
            admission_number=admission_number,
            first_name=first_name,
            last_name=last_name
        )
        messages.success(request, f'Student {admission_number} created successfully.')
        return redirect('administration:student_list')
    return render(request, 'administration/create_student.html')

@login_required
@user_passes_test(is_admin)
def import_students(request):
    """Import students from CSV"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('administration:import_students')
        
        # Create import log
        import_log = StudentImportLog.objects.create(
            admin=request.user,
            filename=csv_file.name,
            status='PROCESSING'
        )
        
        # Process CSV
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            header = next(reader)  # Skip header row
            
            # Check required columns
            required_columns = ['admission_number', 'first_name', 'last_name']
            if not all(column in header for column in required_columns):
                import_log.status = 'FAILED'
                import_log.error_log = 'Missing required columns. CSV must contain: admission_number, first_name, last_name'
                import_log.save()
                messages.error(request, 'CSV format is invalid. Missing required columns.')
                return redirect('administration:import_students')
            
            # Get column indexes
            admission_number_idx = header.index('admission_number')
            first_name_idx = header.index('first_name')
            last_name_idx = header.index('last_name')
            
            # Process rows
            records_total = 0
            records_imported = 0
            records_failed = 0
            error_log = []
            
            for row in reader:
                records_total += 1
                try:
                    if len(row) >= max(admission_number_idx, first_name_idx, last_name_idx) + 1:
                        admission_number = row[admission_number_idx]
                        first_name = row[first_name_idx]
                        last_name = row[last_name_idx]
                        
                        # Create or update student
                        student, created = Student.objects.update_or_create(
                            admission_number=admission_number,
                            defaults={
                                'first_name': first_name,
                                'last_name': last_name
                            }
                        )
                        records_imported += 1
                    else:
                        error_log.append(f'Row {records_total}: Invalid format, missing fields')
                        records_failed += 1
                except Exception as e:
                    error_log.append(f'Row {records_total}: {str(e)}')
                    records_failed += 1
            
            # Update import log
            import_log.status = 'COMPLETED'
            import_log.records_total = records_total
            import_log.records_imported = records_imported
            import_log.records_failed = records_failed
            import_log.error_log = '\n'.join(error_log)
            import_log.save()
            
            # Log action
            log_admin_action(
                request, 
                'IMPORT', 
                'Student', 
                None, 
                f'Imported {records_imported} students from {csv_file.name}'
            )
            
            messages.success(request, f'Successfully imported {records_imported} students. {records_failed} failed.')
        except Exception as e:
            import_log.status = 'FAILED'
            import_log.error_log = str(e)
            import_log.save()
            messages.error(request, f'Error processing CSV: {str(e)}')
        
        return redirect('administration:student_list')
    
    # Display import form
    import_logs = StudentImportLog.objects.order_by('-import_date')[:10]
    
    context = {
        'import_logs': import_logs,
    }
    
    return render(request, 'administration/import_students.html', context)

@login_required
@user_passes_test(is_admin)
def export_students(request):
    """Export students to CSV"""
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    
    # Write CSV
    writer = csv.writer(response)
    writer.writerow(['admission_number', 'first_name', 'last_name'])
    
    students = Student.objects.all()
    for student in students:
        writer.writerow([student.admission_number, student.first_name, student.last_name])
    
    # Log action
    log_admin_action(
        request, 
        'EXPORT', 
        'Student', 
        None, 
        f'Exported {students.count()} students'
    )
    
    return response

@login_required
@user_passes_test(is_admin)
def system_settings(request):
    """Manage system settings"""
    settings = SystemSettings.objects.all()
    
    if request.method == 'POST':
        setting_id = request.POST.get('setting_id')
        setting_value = request.POST.get('setting_value')
        
        # Update setting
        setting = get_object_or_404(SystemSettings, id=setting_id)
        setting.setting_value = setting_value
        setting.save()
        
        # Log action
        log_admin_action(
            request, 
            'UPDATE', 
            'SystemSettings', 
            setting.id, 
            f'Updated {setting.setting_key} to {setting_value}'
        )
        
        messages.success(request, f'Setting {setting.setting_key} updated successfully.')
        return redirect('administration:system_settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'administration/system_settings.html', context)

@login_required
@user_passes_test(is_admin)
def create_setting(request):
    """Create a new system setting"""
    if request.method == 'POST':
        setting_key = request.POST.get('setting_key')
        setting_value = request.POST.get('setting_value')
        description = request.POST.get('description', '')
        
        # Check if setting already exists
        if SystemSettings.objects.filter(setting_key=setting_key).exists():
            messages.error(request, f'Setting {setting_key} already exists.')
            return redirect('administration:create_setting')
        
        # Create setting
        setting = SystemSettings.objects.create(
            setting_key=setting_key,
            setting_value=setting_value,
            description=description
        )
        
        # Log action
        log_admin_action(
            request, 
            'CREATE', 
            'SystemSettings', 
            setting.id, 
            f'Created setting {setting_key} with value {setting_value}'
        )
        
        messages.success(request, f'Setting {setting_key} created successfully.')
        return redirect('administration:system_settings')
    
    return render(request, 'administration/create_setting.html')

@login_required
@user_passes_test(is_admin)
def activity_logs(request):
    """View system activity logs"""
    logs = AdminLog.objects.all().select_related('admin')
    
    # Filter logs
    filter_action = request.GET.get('action')
    filter_user = request.GET.get('user')
    filter_date_start = request.GET.get('date_start')
    filter_date_end = request.GET.get('date_end')
    
    if filter_action:
        logs = logs.filter(action=filter_action)
        
    if filter_user:
        logs = logs.filter(admin__username=filter_user)
        
    if filter_date_start:
        logs = logs.filter(timestamp__date__gte=filter_date_start)
        
    if filter_date_end:
        logs = logs.filter(timestamp__date__lte=filter_date_end)
    
    # Get unique users for filter
    admin_users = User.objects.filter(admin_logs__isnull=False).distinct()
    
    context = {
        'logs': logs[:100],  # Limit to last 100 logs for performance
        'admin_users': admin_users,
        'action_choices': AdminLog.ACTION_CHOICES,
        'filter_action': filter_action,
        'filter_user': filter_user,
        'filter_date_start': filter_date_start,
        'filter_date_end': filter_date_end,
    }
    
    return render(request, 'administration/activity_logs.html', context)

@login_required
@user_passes_test(is_admin)
def session_list(request):
    """List all sessions in the system"""
    # Filter sessions
    filter_course = request.GET.get('course')
    filter_faculty = request.GET.get('faculty')
    filter_date_start = request.GET.get('date_start')
    filter_date_end = request.GET.get('date_end')
    
    sessions = ClassSession.objects.all().select_related('course', 'faculty')
    
    # Apply filters if provided
    if filter_course:
        sessions = sessions.filter(course__course_code=filter_course)
        
    if filter_faculty:
        sessions = sessions.filter(faculty__username=filter_faculty)
        
    if filter_date_start:
        sessions = sessions.filter(date__gte=filter_date_start)
        
    if filter_date_end:
        sessions = sessions.filter(date__lte=filter_date_end)
    
    # Order by date and time
    sessions = sessions.order_by('-date', '-start_time')
    
    # Count attendance for each session
    for session in sessions:
        session.attendance_count = AttendanceRecord.objects.filter(session=session).count()
    
    # Get unique courses and faculty for filters
    courses = Course.objects.all()
    faculty_users = User.objects.filter(sessions__isnull=False).distinct()
    
    context = {
        'sessions': sessions,
        'courses': courses,
        'faculty_users': faculty_users,
        'filter_course': filter_course,
        'filter_faculty': filter_faculty,
        'filter_date_start': filter_date_start,
        'filter_date_end': filter_date_end,
    }
    
    return render(request, 'administration/session_list.html', context)

@login_required
@user_passes_test(is_admin)
def session_detail(request, session_id):
    """View details of a specific session, including attendance records"""
    session = get_object_or_404(ClassSession, id=session_id)
    
    # Get attendance records
    attendance_records = AttendanceRecord.objects.filter(session=session)
    
    context = {
        'session': session,
        'attendance_records': attendance_records,
        'attendance_count': attendance_records.count(),
        'verified_count': attendance_records.filter(is_verified=True).count(),
    }
    
    return render(request, 'administration/session_detail.html', context)
