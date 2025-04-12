from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

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
