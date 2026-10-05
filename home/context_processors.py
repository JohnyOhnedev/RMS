"""Template context processors."""

from django.conf import settings


def site_context(request):
    """Expose small, frequently used values to every template."""
    return {
        "SITE_NAME": "ResumeChecker",
        "ai_enabled": bool(settings.GEMINI_API_KEY),
    }
