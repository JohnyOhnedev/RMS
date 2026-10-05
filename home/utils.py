"""Shared utilities: email notifications and legacy parsing helpers."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail

from home.services.resume_parser import (  # re-exported for backwards compatibility
    extract_text,
    extract_text_from_path,
)

logger = logging.getLogger(__name__)


def send_approval_email(company) -> bool:
    """Email the company owner that their registration was approved.

    Returns True on success. Failures are logged, never raised, so the admin
    approval action always completes.
    """
    recipient = getattr(company.user, "email", "") or ""
    if not recipient:
        logger.warning("No email on file for company '%s'; skipping notification.", company.name)
        return False

    subject = "Your company registration has been approved"
    message = (
        f"Dear {company.name},\n\n"
        "Your company account has been approved by an administrator. "
        "You can now sign in and start managing job roles.\n\n"
        "Best regards,\n"
        "The ResumeChecker Team"
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info("Approval email sent to %s", recipient)
        return True
    except Exception as exc:  # SMTP errors, auth errors, network issues
        logger.error("Failed to send approval email to %s: %s", recipient, exc)
        return False


def parse_resume(file) -> str:
    """Extract text from an uploaded resume file (legacy helper)."""
    return extract_text(file)
