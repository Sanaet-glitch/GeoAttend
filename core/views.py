from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import datetime
from .models import Course, EnrollmentKey

def index(request):
    """Home page view"""
    if request.user.is_authenticated:
        # If user is admin, redirect to admin dashboard first
        if request.user.is_staff or request.user.is_superuser:
            return redirect('administration:dashboard')
        # If user is faculty, redirect to faculty dashboard
        if hasattr(request.user, 'facultyprofile'):
            return redirect('faculty:dashboard')
    # Default to the public landing page
    return render(request, 'core/index.html')

def handler404(request, exception=None):
    return render(request, 'core/404.html', status=404)

def handler500(request):
    return render(request, 'core/500.html', status=500)

@login_required
def manage_enrollment_key(request, course_id):
    """Allow lecturers to create or edit the enrollment key for their course."""
    course = get_object_or_404(Course, id=course_id, lecturers=request.user)
    try:
        enrollment_key = course.enrollment_key
    except EnrollmentKey.DoesNotExist:
        enrollment_key = None

    if request.method == 'POST':
        # Generate a new random key or use provided key
        new_key = request.POST.get('key') or get_random_string(12)
        expires_at_str = request.POST.get('expires_at')
        expires_at = None
        if expires_at_str:
            try:
                expires_at = datetime.strptime(expires_at_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                messages.error(request, 'Invalid expiry date/time format.')
                return redirect('core:manage_enrollment_key', course_id=course.id)
        if 'regenerate' in request.POST and enrollment_key:
            enrollment_key.previous_key = enrollment_key.key
            enrollment_key.key = get_random_string(12)
            enrollment_key.regenerated_at = timezone.now()
            if expires_at:
                enrollment_key.expires_at = expires_at
            enrollment_key.save()
            messages.success(request, 'Enrollment key regenerated.')
        elif enrollment_key:
            enrollment_key.key = new_key
            enrollment_key.expires_at = expires_at
            enrollment_key.save()
            messages.success(request, 'Enrollment key updated.')
        else:
            EnrollmentKey.objects.create(course=course, key=new_key, created_by=request.user, expires_at=expires_at)
            messages.success(request, 'Enrollment key created.')
        return redirect('core:manage_enrollment_key', course_id=course.id)

    return render(request, 'core/manage_enrollment_key.html', {
        'course': course,
        'enrollment_key': enrollment_key,
    })

def redirect_logged_in_user(request):
    """Redirect logged-in users away from the login page based on role."""
    if request.user.is_authenticated:
        # Admin users go to the admin dashboard
        if request.user.is_staff or request.user.is_superuser:
            return redirect('administration:dashboard')
        # Faculty users go to the faculty dashboard
        if hasattr(request.user, 'facultyprofile'):
            return redirect('faculty:dashboard')
        # Other authenticated users go to home
        return redirect('core:index')
    return None
