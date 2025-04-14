from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from .models import Course, EnrollmentKey

def index(request):
    """Home page view"""
    if request.user.is_authenticated:
        # If user is faculty, redirect to faculty dashboard
        if hasattr(request.user, 'facultyprofile'):
            return redirect('faculty:dashboard')
        # If user is admin, redirect to admin dashboard
        elif request.user.is_staff:
            return redirect('administration:dashboard')
    
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
        if enrollment_key:
            enrollment_key.key = new_key
            enrollment_key.save()
            messages.success(request, 'Enrollment key updated.')
        else:
            EnrollmentKey.objects.create(course=course, key=new_key, created_by=request.user)
            messages.success(request, 'Enrollment key created.')
        return redirect('core:manage_enrollment_key', course_id=course.id)

    return render(request, 'core/manage_enrollment_key.html', {
        'course': course,
        'enrollment_key': enrollment_key,
    })
