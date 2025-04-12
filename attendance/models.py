from django.db import models
from django.utils import timezone
from core.models import ClassSession

class Student(models.Model):
    """Model representing a student"""
    roll_number = models.CharField(max_length=20, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.roll_number} - {self.first_name} {self.last_name}"

class AttendanceRecord(models.Model):
    """Model for tracking student attendance"""
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    
    # Verification data
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Status information
    is_verified = models.BooleanField(default=True)
    verification_method = models.CharField(max_length=20, default="GPS")
    distance_from_class = models.FloatField(null=True, blank=True)  # Distance in meters
    
    # Flags
    flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ['session', 'student']  # Prevent duplicate attendance
        
    def __str__(self):
        return f"{self.student} - {self.session} - {'✓' if self.is_verified else '✗'}"
