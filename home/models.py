from django.db import models

# Create your models here.
# models.py
from django.db import models

#from django.db import models

class UserResume(models.Model):
    uploaded_file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField()
    prediction = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    

from django.contrib.auth.models import User
from django.db import models

# Choices for approval status
APPROVAL_STATUS = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



from django.db import models

class ResumeEntry(models.Model):
    uploaded_file = models.FileField(upload_to="resumes/")
    resume_hash = models.CharField(max_length=64, unique=True)  # SHA-256 hash to prevent duplicates
    extracted_text = models.TextField()  # Store parsed text for searching
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume {self.id} - {self.uploaded_at}"