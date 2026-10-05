"""Small reusable helpers for views and services."""

from __future__ import annotations

import hashlib
import logging

from django.contrib import messages

logger = logging.getLogger(__name__)


def sha256_of_uploaded_file(uploaded_file) -> str:
    """Return the SHA-256 hex digest of an uploaded file without consuming it."""
    digest = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        digest.update(chunk)
    uploaded_file.seek(0)
    return digest.hexdigest()


def flash_form_errors(request, form) -> None:
    """Surface every form error through the messages framework."""
    for field, errors in form.errors.items():
        label = form.fields[field].label if field in form.fields else field
        for error in errors:
            messages.error(request, f"{label}: {error}")


def get_client_ip(request) -> str:
    """Best-effort client IP for logging."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")
