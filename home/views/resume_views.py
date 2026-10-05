"""Resume upload, analysis, job-role prediction and resource views."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from home.forms import ResumeUploadForm
from home.models import ResumeEntry, UserResume
from home.services import ai_service, job_predictor, recommender
from home.services.exceptions import AIUnavailableError, ResumeServiceError
from home.services.helpers import get_client_ip, sha256_of_uploaded_file
from home.services.resume_analyzer import analyse_resume
from home.services.resume_parser import extract_text
from home.services.skill_extractor import extract_skills

logger = logging.getLogger(__name__)


def _read_upload(request):
    """Validate, parse and return (uploaded_file, text) or raise ResumeServiceError."""
    upload = request.FILES.get("resume") or request.FILES.get("file")
    if upload is None:
        raise ResumeServiceError("No file was uploaded. Please choose a resume file.")

    # Build the form with ``files`` populated so Django's FileField validation
    # runs (passing a plain dict makes the field always report "required").
    form = ResumeUploadForm(data=request.POST or None, files={"file": upload})
    if not form.is_valid():
        message = " ".join(
            error for errors in form.errors.values() for error in errors
        )
        raise ResumeServiceError(message or "That file could not be accepted.")

    return upload, extract_text(upload)


@require_http_methods(["GET", "POST"])
def process_resume(request):
    """Full resume review: ATS score + skills + AI narrative."""
    if request.method == "POST":
        try:
            upload, resume_text = _read_upload(request)
        except ResumeServiceError as exc:
            messages.error(request, str(exc))
            return render(request, "upload.html", {"form": ResumeUploadForm()})

        analysis = analyse_resume(resume_text)

        ai_review = None
        try:
            ai_review = ai_service.review_resume(resume_text, analysis)
        except AIUnavailableError as exc:
            logger.warning("AI review failed: %s", exc)
            messages.warning(request, "AI review is temporarily unavailable; showing local analysis.")

        UserResume.objects.create(
            uploaded_file=upload,
            extracted_text=resume_text,
            prediction=str(analysis.score),
        )

        context = {
            "analysis": analysis,
            "recommendations": ai_review or "",
            "resume_text": resume_text,
            "ai_used": ai_service.is_configured(),
        }
        return render(request, "result.html", context)

    return render(request, "upload.html", {"form": ResumeUploadForm()})


@require_http_methods(["GET", "POST"])
def upload_resume2(request):
    """Predict the best-matching job roles for an uploaded resume."""
    if request.method == "POST":
        try:
            upload, resume_text = _read_upload(request)
        except ResumeServiceError as exc:
            messages.error(request, str(exc))
            return render(request, "upload_resume.html", {"error": str(exc)})

        predictions = job_predictor.predict_job_roles(resume_text)

        UserResume.objects.create(
            uploaded_file=upload,
            extracted_text=resume_text,
            prediction=str(predictions),
        )

        return render(
            request,
            "upload_resume.html",
            {
                "predictions": predictions,
                "skills": extract_skills(resume_text)[:20],
                "resume_text": resume_text,
            },
        )

    return render(request, "upload_resume.html", {"form": ResumeUploadForm()})


@require_http_methods(["GET", "POST"])
def process_resume2(request):
    """Build an interview plan from an uploaded resume."""
    if request.method == "POST":
        try:
            _, resume_text = _read_upload(request)
        except ResumeServiceError as exc:
            messages.error(request, str(exc))
            return render(request, "upload4.html", {"form": ResumeUploadForm()})

        try:
            plan = ai_service.build_interview_plan(resume_text)
        except AIUnavailableError as exc:
            logger.warning("Interview plan failed: %s", exc)
            messages.warning(request, "Interview plan service unavailable; showing local fallback.")
            plan = ""

        return render(
            request,
            "result2.html",
            {"recommendations": plan, "ai_used": ai_service.is_configured()},
        )

    return render(request, "upload4.html", {"form": ResumeUploadForm()})


@require_http_methods(["GET", "POST"])
def recommend_resources(request):
    """Recommend learning resources based on skills detected in the resume."""
    if request.method == "POST":
        try:
            _, resume_text = _read_upload(request)
        except ResumeServiceError as exc:
            messages.error(request, str(exc))
            return render(request, "upload3.html", {"form": ResumeUploadForm()})

        context = recommender.recommend_resources(resume_text)
        return render(request, "resources.html", context)

    return render(request, "upload3.html", {"form": ResumeUploadForm()})


# ----- Backwards-compatible aliases (old URL names) ----------------------------
upload_resume = process_resume


@require_http_methods(["GET", "POST"])
def upload_resume_dedup(request):
    """Upload a resume with SHA-256 duplicate detection (ResumeEntry model)."""
    if request.method == "POST":
        upload = request.FILES.get("resume") or request.FILES.get("file")
        if upload is None:
            return JsonResponse({"error": "No file uploaded."}, status=400)

        try:
            file_hash = sha256_of_uploaded_file(upload)
        except Exception as exc:  # pragma: no cover - IO failure
            logger.error("Hashing failed: %s", exc)
            return JsonResponse({"error": "Could not read the uploaded file."}, status=400)

        if ResumeEntry.objects.filter(resume_hash=file_hash).exists():
            return JsonResponse(
                {"error": "Duplicate resume detected - this file was already uploaded."},
                status=409,
            )

        try:
            resume_text = extract_text(upload)
        except ResumeServiceError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        entry = ResumeEntry(resume_hash=file_hash, extracted_text=resume_text)
        upload.seek(0)
        entry.uploaded_file.save(upload.name, upload, save=False)
        entry.save()

        logger.info("Resume stored (hash=%s) from %s", file_hash[:12], get_client_ip(request))
        return JsonResponse({"message": "Resume uploaded successfully.", "id": entry.pk})

    return render(request, "upload_resume5.html", {"form": ResumeUploadForm()})
