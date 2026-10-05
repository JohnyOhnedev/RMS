"""Database models for the RMS (Resume Management System)."""

from django.contrib.auth.models import User
from django.db import models


# Choices for company approval status
APPROVAL_STATUS = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


class UserResume(models.Model):
    """A candidate resume uploaded for job-role prediction."""

    uploaded_file = models.FileField(upload_to="resumes/")
    extracted_text = models.TextField(blank=True, default="")
    prediction = models.TextField(blank=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Predicted resume"
        verbose_name_plural = "Predicted resumes"
        indexes = [models.Index(fields=["-uploaded_at"])]

    def __str__(self) -> str:
        return f"Resume {self.pk} - {self.uploaded_at:%Y-%m-%d %H:%M}"

    @property
    def filename(self) -> str:
        return self.uploaded_file.name.rsplit("/", 1)[-1] if self.uploaded_file else ""

    @property
    def top_role(self) -> str:
        """Best-guess job role from the stored prediction string."""
        try:
            import ast

            parsed = ast.literal_eval(self.prediction)
            if parsed:
                return parsed[0][0]
        except (ValueError, SyntaxError, IndexError, TypeError):
            pass
        return "Unknown"


class Company(models.Model):
    """A recruiting company account pending (or granted) admin approval."""

    name = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
    approval_status = models.CharField(
        max_length=10, choices=APPROVAL_STATUS, default="pending", db_index=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name_plural = "Companies"

    def __str__(self) -> str:
        return self.name

    @property
    def is_approved(self) -> bool:
        return self.approval_status == "approved"


class ResumeEntry(models.Model):
    """A resume stored under a content hash to prevent duplicate submissions."""

    uploaded_file = models.FileField(upload_to="resumes/")
    resume_hash = models.CharField(
        max_length=64, unique=True, help_text="SHA-256 hash to prevent duplicates"
    )
    extracted_text = models.TextField(blank=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Resume entry"
        verbose_name_plural = "Resume entries"

    def __str__(self) -> str:
        return f"Resume {self.pk} - {self.uploaded_at:%Y-%m-%d %H:%M}"
