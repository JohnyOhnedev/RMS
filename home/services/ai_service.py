"""Google Gemini integration with a fully offline fallback.

The original code hard-coded an API key in views.py, pinned retired model
names (gemini-1.5-pro-latest / gemini-1.5-pro) and crashed the whole request
when the API was unavailable. Here:

  * the key and model names come from settings (env-driven),
  * the google-generativeai SDK is imported lazily,
  * any failure falls back to a deterministic, locally generated report so the
    user still gets useful output.
"""

from __future__ import annotations

import logging

from django.conf import settings

from .exceptions import AIUnavailableError
from .resume_analyzer import AnalysisResult

logger = logging.getLogger(__name__)

_client = None
_client_configured = False


def is_configured() -> bool:
    """True when a Gemini API key has been provided."""
    return bool(settings.GEMINI_API_KEY)


def _get_model(model_name: str):
    """Lazily build a GenerativeModel, caching the SDK configuration."""
    global _client, _client_configured

    if not is_configured():
        raise AIUnavailableError("No Gemini API key configured.")

    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise AIUnavailableError(
            "google-generativeai is not installed. Run: pip install google-generativeai"
        ) from exc

    if not _client_configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _client_configured = True

    return genai.GenerativeModel(model_name)


def _generate(prompt: str, model_name: str) -> str:
    """Call Gemini and return the text, raising AIUnavailableError on failure."""
    try:
        model = _get_model(model_name)
        response = model.generate_content(prompt)
        text = (getattr(response, "text", "") or "").strip()
        if not text:
            raise AIUnavailableError("The AI returned an empty response.")
        return text
    except AIUnavailableError:
        raise
    except Exception as exc:  # network, quota, safety block, retired model...
        logger.warning("Gemini call failed (%s): %s", model_name, exc)
        raise AIUnavailableError(str(exc)) from exc


# ---------------------------------------------------------------------------
# Resume review
# ---------------------------------------------------------------------------
REVIEW_PROMPT = """You are an experienced technical career counsellor and ATS specialist.
Review the resume text below and respond in clean Markdown with these sections:

## Overall Impression
## Strengths
## Weaknesses
## Section-by-Section Improvements
(Summary, Education, Skills, Experience, Projects, Certifications - skip any that are absent)
## ATS & Keyword Advice
## Three Highest-Impact Next Actions

Be specific and actionable. Quote the candidate's own wording when suggesting rewrites.

Resume text:
\"\"\"{resume_text}\"\"\"
"""


def review_resume(resume_text: str, analysis: AnalysisResult | None = None) -> str:
    """Return an AI review, or a local fallback report if AI is unavailable."""
    if is_configured():
        try:
            return _generate(
                REVIEW_PROMPT.format(resume_text=resume_text[:20000]),
                settings.GEMINI_MODEL,
            )
        except AIUnavailableError as exc:
            logger.info("Falling back to local review: %s", exc)

    if not settings.AI_FALLBACK_ENABLED:
        raise AIUnavailableError("AI review unavailable and fallback is disabled.")

    return _local_review(resume_text, analysis)


def _local_review(resume_text: str, analysis: AnalysisResult | None) -> str:
    """Deterministic markdown report generated without any API call."""
    from .resume_analyzer import analyse_resume

    result = analysis or analyse_resume(resume_text)

    lines: list[str] = [
        "## Overall Impression",
        f"Automated analysis scored this resume **{result.score}/100 ({result.grade})** "
        f"across contact details, structure, skills, experience, education and measurable impact.",
        "",
        "## Strengths",
    ]

    strengths = result.good_findings
    if strengths:
        lines += [f"- {finding.message}" for finding in strengths]
    else:
        lines.append("- Nothing stood out as a clear strength yet - see the actions below.")

    lines += ["", "## Weaknesses"]
    weaknesses = result.problems + result.warnings
    if weaknesses:
        lines += [f"- {finding.message}" for finding in weaknesses]
    else:
        lines.append("- No significant weaknesses detected.")

    lines += ["", "## Section-by-Section Improvements"]
    for section, present in result.sections.items():
        state = "present" if present else "**missing**"
        lines.append(f"- {section.title()}: {state}")

    lines += ["", "## Detected Skills"]
    if result.skills_by_category:
        for category, skills in sorted(result.skills_by_category.items()):
            lines.append(f"- {category}: {', '.join(skills)}")
    else:
        lines.append("- No recognisable technical skills were detected.")

    lines += ["", "## ATS & Keyword Advice"]
    lines += [
        "- Use a single-column layout with standard headings (Experience, Education, Skills).",
        "- Mirror the exact keywords in each job advert you apply to.",
        "- Avoid tables, text boxes and images for critical information - parsers skip them.",
        "- Save as PDF (text-based, not scanned) unless the employer asks for .docx.",
    ]

    lines += ["", "## Three Highest-Impact Next Actions"]
    top = result.suggestions[:3]
    lines += [f"{index}. {tip}" for index, tip in enumerate(top, start=1)]

    lines.append("")
    lines.append(
        "_Generated locally without AI. Set `GEMINI_API_KEY` in `.env` for a personalised AI review._"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interview plan
# ---------------------------------------------------------------------------
INTERVIEW_PROMPT = """You are a hiring manager preparing an interview for the candidate below.
Produce a structured interview plan in Markdown with:

## Candidate Snapshot
## Technical Questions (8, tailored to the listed skills, with what to listen for)
## Behavioural Questions (5, mapped to real experience)
## Soft Skills & Culture-Fit Questions (4)
## Suggested Coding / Practical Task
## Red Flags To Probe

Resume text:
\"\"\"{resume_text}\"\"\"
"""


def build_interview_plan(resume_text: str) -> str:
    """Return an interview plan, or a local fallback when AI is unavailable."""
    if is_configured():
        try:
            return _generate(
                INTERVIEW_PROMPT.format(resume_text=resume_text[:20000]),
                settings.GEMINI_MODEL_INTERVIEW,
            )
        except AIUnavailableError as exc:
            logger.info("Falling back to local interview plan: %s", exc)

    if not settings.AI_FALLBACK_ENABLED:
        raise AIUnavailableError("AI interview plan unavailable and fallback is disabled.")

    return _local_interview_plan(resume_text)


def _local_interview_plan(resume_text: str) -> str:
    from .skill_extractor import extract_skills

    skills = extract_skills(resume_text)
    focus_skills = skills[:6] or ["general programming", "problem solving", "teamwork"]

    lines: list[str] = ["## Candidate Snapshot"]
    lines.append(
        f"Detected {len(skills)} skills. Interview should focus on: {', '.join(focus_skills)}."
    )

    lines += ["", "## Technical Questions"]
    for index, skill in enumerate(focus_skills, start=1):
        lines.append(
            f"{index}. Walk me through a project where you used **{skill}**. "
            f"What was the hardest part and how did you debug it?"
        )

    lines += ["", "## Behavioural Questions"]
    lines += [
        "1. Tell me about a time you disagreed with a teammate. How was it resolved?",
        "2. Describe your most challenging deadline and how you handled it.",
        "3. Give an example of feedback that changed how you work.",
        "4. Describe a mistake you made and what you learned.",
        "5. Tell me about a time you had to learn something quickly on your own.",
    ]

    lines += ["", "## Soft Skills & Culture-Fit Questions"]
    lines += [
        "1. How do you prefer to receive feedback?",
        "2. How do you prioritise when everything is urgent?",
        "3. What kind of work environment brings out your best?",
        "4. Where do you want to grow in the next two years?",
    ]

    lines += [
        "",
        "## Suggested Coding / Practical Task",
        f"Ask the candidate to extend a small feature in {focus_skills[0]} end to end, "
        "including a test and a short written explanation of trade-offs.",
        "",
        "## Red Flags To Probe",
        "- Claims of team achievements with no personal contribution.",
        "- Skills listed that never appear in any project description.",
        "- Unexplained gaps between dated roles.",
        "",
        "_Generated locally without AI. Set `GEMINI_API_KEY` in `.env` for a tailored plan._",
    ]
    return "\n".join(lines)
