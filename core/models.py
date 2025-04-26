from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
import base64

SEMESTER_CHOICES = [
    ("Jan-Apr", "January - April"),
    ("May-Aug", "May - August"),
    ("Sep-Dec", "September - December"),
]

class Course(models.Model):
    """Model representing an academic course."""
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lecturers = models.ManyToManyField(User, related_name="courses")  # Link courses to specific lecturers
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_code}: {self.title}"


class ClassSession(models.Model):
    """Model representing a specific class meeting."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    semester = models.CharField(max_length=7, choices=SEMESTER_CHOICES, default="Jan-Apr")  # Add semester field

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"{self.course} - {self.title} ({self.date})"

    def get_qr_code(self, request=None):
        """Generate a QR code for this session with extra session info."""
        import json
        
        # Make sure we have a request object for proper URL generation
        if request is None:
            # Fallback to settings.BASE_URL only if no request is provided
            # This should rarely happen with our improved implementation
            from django.conf import settings
            base_url = settings.BASE_URL
            attendance_url = f"{base_url}/attendance/mark/{self.session_key}/"
        else:
            # Generate a fully qualified URL including the correct host/domain
            # This is critical for QR codes to work across devices on the same network
            attendance_url = request.build_absolute_uri(f"/attendance/mark/{self.session_key}/")
        
        # Prepare session info with detailed data for better debugging
        session_info = {
            'session_key': str(self.session_key),
            'course_code': self.course.course_code,
            'course_title': self.course.title,
            'date': self.date.strftime('%Y-%m-%d'),
            'start_time': self.start_time.strftime('%H:%M'),
            'url': attendance_url
        }
        
        # Use a more concise data format for the QR code
        # Instead of full JSON, just use the URL directly for better compatibility
        qr_data = attendance_url
        
        # Generate QR code with error correction for better scanning
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for embedding in web page
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def get_status(self):
        """Return session status: Inactive, Active, or Ended based on current time."""
        from django.utils import timezone
        from datetime import datetime
        now = timezone.localtime(timezone.now())
        start_dt = timezone.make_aware(datetime.combine(self.date, self.start_time))
        end_dt = timezone.make_aware(datetime.combine(self.date, self.end_time))
        if now < start_dt:
            return "Inactive"
        elif start_dt <= now <= end_dt:
            return "Active"
        else:
            return "Ended"


class EnrollmentKey(models.Model):
    """Model for course enrollment keys, managed by lecturers."""
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name="enrollment_key")
    key = models.CharField(max_length=32, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_enrollment_keys")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    regenerated_at = models.DateTimeField(null=True, blank=True)
    previous_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return f"Key for {self.course.course_code}"


class Enrollment(models.Model):
    """Model for student enrollment in courses."""
    student = models.ForeignKey('attendance.Student', on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} enrolled in {self.course.course_code}"
