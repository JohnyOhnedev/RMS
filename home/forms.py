"""Forms for the RMS application."""

from django import forms
from django.conf import settings
from django.contrib.auth.models import User

from .models import Company


class SignupForm(forms.ModelForm):
    """Candidate signup form with password confirmation and validation."""

    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label="Confirm password",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmation = cleaned_data.get("password_confirmation")

        if password and confirmation and password != confirmation:
            self.add_error("password_confirmation", "Passwords do not match.")

        if password:
            from django.contrib.auth.password_validation import validate_password

            try:
                validate_password(password)
            except forms.ValidationError as exc:
                self.add_error("password", exc)

        return cleaned_data


class CompanySignupForm(forms.Form):
    """Company self-registration form."""

    company_name = forms.CharField(max_length=255)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label="Confirm password",
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_company_name(self):
        name = self.cleaned_data["company_name"].strip()
        if Company.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A company with this name is already registered.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmation = cleaned_data.get("password_confirmation")
        if password and confirmation and password != confirmation:
            self.add_error("password_confirmation", "Passwords do not match.")
        return cleaned_data


class ResumeUploadForm(forms.Form):
    """Resume upload with extension and size validation."""

    file = forms.FileField(label="Upload your resume", required=True)

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        name = (uploaded.name or "").lower()

        if not any(name.endswith(ext) for ext in settings.ALLOWED_RESUME_EXTENSIONS):
            allowed = ", ".join(settings.ALLOWED_RESUME_EXTENSIONS)
            raise forms.ValidationError(f"Unsupported file type. Allowed: {allowed}")

        if uploaded.size > settings.MAX_RESUME_UPLOAD_SIZE:
            limit_mb = settings.MAX_RESUME_UPLOAD_SIZE / (1024 * 1024)
            raise forms.ValidationError(f"File is too large. Maximum size is {limit_mb:.0f} MB.")

        return uploaded


class FileUploadForm(forms.Form):
    """Generic file upload form (kept for backwards compatibility)."""

    file = forms.FileField(label="Upload a file (PDF, DOCX, TXT)", required=True)
