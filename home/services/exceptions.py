"""Consistent, expressive errors for the service layer."""


class ResumeServiceError(Exception):
    """Base class for resume processing errors."""


class UnsupportedFileType(ResumeServiceError):
    """Raised when an uploaded file is not a supported resume format."""


class EmptyResumeError(ResumeServiceError):
    """Raised when no text could be extracted from the resume."""


class AIUnavailableError(ResumeServiceError):
    """Raised when an AI provider is required but not configured/reachable."""
