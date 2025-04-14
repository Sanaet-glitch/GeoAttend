from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
import base64


class Course(models.Model):
    """Model representing an academic course"""
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.course_code}: {self.title}"


class ClassSession(models.Model):
    """Model representing a specific class meeting"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Session status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"{self.course} - {self.title} ({self.date})"
    
    def get_qr_code(self):
        """Generate a QR code for this session with extra session info"""
        from django.conf import settings
        import json
        # Prepare session info
        session_info = {
            'session_key': str(self.session_key),
            'course_code': self.course.course_code,
            'course_title': self.course.title,
            'date': self.date.strftime('%Y-%m-%d'),
            'start_time': self.start_time.strftime('%H:%M'),
            'url': f"{settings.BASE_URL}/api/attendance/mark/{self.session_key}/"
        }
        qr_data = json.dumps(session_info)
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
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
