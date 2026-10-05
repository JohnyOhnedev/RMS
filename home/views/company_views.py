"""Company signup/login, dashboard and the admin approval workflow."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from home.forms import CompanySignupForm
from home.models import Company
from home.services import job_predictor
from home.utils import send_approval_email

logger = logging.getLogger(__name__)


def is_admin(user) -> bool:
    """Predicate used by ``user_passes_test``."""
    return bool(user.is_authenticated and user.is_staff)


def company_signup(request):
    """Register a new company account (awaits admin approval)."""
    if request.method == "POST":
        form = CompanySignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
            )
            Company.objects.create(user=user, name=data["company_name"], approval_status="pending")
            logger.info("Company '%s' registered (user=%s)", data["company_name"], user.username)
            return render(
                request,
                "company_signup.html",
                {
                    "form": CompanySignupForm(),
                    "message": "Signup successful! Your account is awaiting admin approval.",
                },
            )
        messages.error(request, "Please correct the errors below.")
    else:
        form = CompanySignupForm()

    return render(request, "company_signup.html", {"form": form})


def company_login(request):
    """Log an approved company in."""
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(
                request, "company_login.html", {"error": "Invalid username or password."}
            )

        company = Company.objects.filter(user=user).first()
        if company is None:
            return render(
                request, "company_login.html", {"error": "No company account is linked to this user."}
            )

        if company.approval_status == "approved":
            login(request, user)
            return redirect("home:company_dashboard")

        if company.approval_status == "rejected":
            return render(
                request,
                "company_login.html",
                {"error": "Your company registration was rejected. Please contact support."},
            )

        return render(
            request, "company_login.html", {"error": "Your company is still awaiting approval."}
        )

    return render(request, "company_login.html")


@login_required
def company_dashboard(request):
    """Company workspace: manage job roles and their required skills."""
    if request.method == "POST":
        job_role = (request.POST.get("job_role") or "").strip()
        skills = (request.POST.get("skills") or "").strip()

        try:
            message = job_predictor.add_or_update_role(job_role, skills)
            messages.success(request, message)
        except ValueError as exc:
            messages.error(request, str(exc))

        return redirect("home:company_dashboard")

    requested_role = (request.GET.get("job_role") or "").strip()
    current_skills = job_predictor.get_skills_for_role(requested_role) if requested_role else ""

    return render(
        request,
        "dashboard.html",
        {
            "data": job_predictor.load_job_data(),
            "current_skills": current_skills,
            "job_role": requested_role,
        },
    )


@login_required
def dashboard(request):
    """Legacy candidate/company router kept for URL compatibility."""
    company = Company.objects.filter(user=request.user).first()
    if company and company.approval_status != "approved":
        return render(request, "approval_pending.html")
    return redirect("home:company_dashboard")


@login_required
@user_passes_test(is_admin, login_url="/admin/login/")
def review_queue(request):
    """Admin-only queue for approving or rejecting company registrations."""
    pending = Company.objects.filter(approval_status="pending")

    if request.method == "POST":
        processed = 0
        for company in pending:
            decision = request.POST.get(f"company_{company.id}")
            if decision == "approve":
                company.approval_status = "approved"
                company.save(update_fields=["approval_status"])
                try:
                    send_approval_email(company)
                except Exception as exc:  # email must never break approvals
                    logger.error("Approval email failed for %s: %s", company.name, exc)
                messages.success(request, f"{company.name} has been approved.")
                processed += 1
            elif decision == "reject":
                company.approval_status = "rejected"
                company.save(update_fields=["approval_status"])
                messages.success(request, f"{company.name} has been rejected.")
                processed += 1

        if processed == 0:
            messages.info(request, "No decisions were submitted.")
        return redirect("home:review_queue")

    return render(request, "review_queue.html", {"companies": pending})


def fetch_skills(request):
    """JSON endpoint used by the dashboard to prefill existing skills."""
    job_role = (request.GET.get("job_role") or "").strip()
    return JsonResponse({"skills": job_predictor.get_skills_for_role(job_role)})


@login_required
@user_passes_test(is_admin, login_url="/admin/login/")
@require_POST
def import_job_data(request):
    """Import additional job-role data from a JSON upload (admin only)."""
    import json

    upload = request.FILES.get("job_data")
    if upload is None:
        messages.error(request, "Please choose a JSON file to import.")
        return redirect("home:review_queue")

    try:
        payload = json.load(upload)
        if not isinstance(payload, dict):
            raise ValueError("The JSON root must be an object of {role: skills}.")
    except (ValueError, json.JSONDecodeError) as exc:
        messages.error(request, f"Invalid JSON: {exc}")
        return redirect("home:review_queue")

    current = job_predictor.load_job_data()
    current.update({str(role): str(skills) for role, skills in payload.items()})
    job_predictor.save_job_data(current)

    messages.success(request, f"Imported {len(payload)} job role(s).")
    return redirect("home:company_dashboard")
