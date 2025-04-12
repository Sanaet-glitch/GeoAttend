from django.db import models
from django.contrib.auth.models import User
from core.models import Course

class FacultyProfile(models.Model):
    """Extended profile for faculty members"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class CourseAssignment(models.Model):
    """Mapping between faculty members and courses they teach"""
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name='course_assignments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='faculty_assignments')
    semester = models.CharField(max_length=20)
    year = models.IntegerField()
    
    class Meta:
        unique_together = ['faculty', 'course', 'semester', 'year']
        
    def __str__(self):
        return f"{self.course} - {self.faculty} ({self.semester} {self.year})"
