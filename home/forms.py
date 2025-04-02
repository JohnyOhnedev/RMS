from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirmation = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password != password_confirmation:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
    


class ResumeUploadForm(forms.Form):
    file = forms.FileField(label='Upload your resume', required=True)



from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField(label='Upload a file (PDF, JPG, PNG)', required=True)
