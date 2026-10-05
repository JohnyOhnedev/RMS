"""Authentication and landing-page views."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from home.forms import SignupForm

logger = logging.getLogger(__name__)


def home(request):
    """Landing page with the quick resume-match widget."""
    if request.method == "POST" and request.FILES.get("file"):
        from home.services.resume_parser import extract_text
        from home.services.exceptions import ResumeServiceError
        from home.services.skill_extractor import extract_skills
        from home.services.job_predictor import predict_job_roles

        uploaded = request.FILES["file"]
        try:
            text = extract_text(uploaded)
        except ResumeServiceError as exc:
            messages.error(request, str(exc))
            return render(request, "home.html")

        request.session["match_text"] = text[:20000]
        context = {
            "skills": extract_skills(text)[:20],
            "predictions": predict_job_roles(text),
            "analysis": True,
        }
        return render(request, "home.html", context)

    if request.method == "POST":
        messages.error(request, "Please choose a file to upload.")

    return render(request, "home.html")


def login_view(request):
    """Log a candidate in and route them appropriately."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("home:review_queue")
        return redirect("home:afterlogin")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_short_name() or user.username}!")
            if user.is_staff:
                return redirect("home:review_queue")
            return redirect("home:afterlogin")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def signup_view(request):
    """Candidate registration."""
    if request.user.is_authenticated:
        return redirect("home:afterlogin")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            if not user.email:
                user.email = ""
            user.save()
            login(request, user)
            messages.success(request, "Account created successfully. You are now logged in.")
            return redirect("home:afterlogin")
        messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


def logout_view(request):
    """Log out and return to the landing page."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("home:home")


@login_required
def afterlogin_view(request):
    """Candidate landing page shown after login."""
    return render(request, "afterlogin.html")


def features(request):
    """Marketing/feature overview page."""
    return render(request, "features.html")
