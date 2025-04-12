from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SystemSettings(models.Model):
    """Global system configuration settings"""
    setting_key = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.setting_key

class AdminLog(models.Model):
    """Log of administrative actions"""
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('IMPORT', 'Import'),
        ('EXPORT', 'Export'),
        ('LOGIN', 'Login'),
        ('OTHER', 'Other'),
    ]
    
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True, null=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.admin} - {self.action} {self.object_type} - {self.timestamp}"

class StudentImportLog(models.Model):
    """Record of student data imports"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='import_logs')
    filename = models.CharField(max_length=255)
    import_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    records_total = models.IntegerField(default=0)
    records_imported = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.filename} - {self.import_date} - {self.status}"
