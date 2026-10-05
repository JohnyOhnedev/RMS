"""Deterministic resume quality analysis (ATS-style scoring).

This runs offline with no external API, so the "Analyze resume" feature is
always available. When a Gemini API key is configured the AI narrative is
layered on top of these findings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .skill_extractor import categorise_skills, detect_sections, extract_skills

# Weights must sum to 100.
WEIGHTS = {
    "contact": 15,
    "sections": 25,
    "skills": 20,
    "experience": 20,
    "education": 10,
    "impact": 10,
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:(?:\+|00)\d{1,3}[\s-]?)?(?:\d[\s-]?){9,12}\d")
URL_RE = re.compile(r"(?:https?://|www\.)\S+|linkedin\.com/\S+|github\.com/\S+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
METRIC_RE = re.compile(
    r"\b\d+\s?(?:%|percent|k\b|x\b|\+)|(?:\$|₹|€)\s?\d", re.IGNORECASE
)
ACTION_VERBS = (
    "built", "developed", "designed", "implemented", "led", "managed", "created",
    "improved", "increased", "reduced", "optimized", "optimised", "launched",
    "delivered", "automated", "migrated", "achieved", "coordinated", "architected",
    "mentored", "analysed", "analyzed", "deployed", "integrated", "collaborated",
)


@dataclass
class Finding:
    """A single observation about the resume."""

    category: str
    status: str  # "good" | "warn" | "bad"
    message: str


@dataclass
class AnalysisResult:
    """Structured result of the heuristic resume analysis."""

    score: int = 0
    subscores: dict[str, int] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    skills_by_category: dict[str, list[str]] = field(default_factory=dict)
    sections: dict[str, bool] = field(default_factory=dict)
    word_count: int = 0
    suggestions: list[str] = field(default_factory=list)

    @property
    def subscore_rows(self) -> list[dict]:
        """Subscores as display rows: label, points, max, and percentage.

        The raw subscores are points out of each dimension's weight (e.g. 25/25),
        so a percentage has to be derived for progress bars. Computing it here
        keeps templates dumb and prevents the 250%-width bug.
        """
        rows = []
        for name, points in self.subscores.items():
            maximum = WEIGHTS.get(name, 0)
            percent = round(points / maximum * 100) if maximum else 0
            rows.append(
                {
                    "name": name,
                    "label": name.replace("_", " ").capitalize(),
                    "points": points,
                    "max": maximum,
                    "percent": max(0, min(100, percent)),
                }
            )
        return rows

    @property
    def grade(self) -> str:
        if self.score >= 85:
            return "Excellent"
        if self.score >= 70:
            return "Good"
        if self.score >= 55:
            return "Fair"
        return "Needs work"

    @property
    def good_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.status == "good"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.status == "warn"]

    @property
    def problems(self) -> list[Finding]:
        return [f for f in self.findings if f.status == "bad"]


def _score_contact(text: str, result: AnalysisResult) -> int:
    points = 0
    if EMAIL_RE.search(text):
        points += 6
        result.findings.append(Finding("Contact", "good", "Email address found."))
    else:
        result.findings.append(
            Finding("Contact", "bad", "No email address found. Recruiters need a way to reach you.")
        )

    if PHONE_RE.search(text):
        points += 5
        result.findings.append(Finding("Contact", "good", "Phone number found."))
    else:
        result.findings.append(Finding("Contact", "warn", "No phone number detected."))

    if URL_RE.search(text):
        points += 4
        result.findings.append(
            Finding("Contact", "good", "Online profile or portfolio link found (LinkedIn/GitHub/website).")
        )
    else:
        result.findings.append(
            Finding(
                "Contact",
                "warn",
                "No LinkedIn/GitHub/portfolio link. Adding one strengthens your application.",
            )
        )
    return min(points, WEIGHTS["contact"])


def _score_sections(result: AnalysisResult) -> int:
    for section, present in result.sections.items():
        if present:
            result.findings.append(Finding("Structure", "good", f"'{section.title()}' section detected."))
        else:
            severity = "warn" if section in {"projects", "certifications", "summary"} else "bad"
            result.findings.append(
                Finding("Structure", severity, f"No '{section.title()}' section heading detected.")
            )

    present_count = sum(1 for present in result.sections.values() if present)
    ratio = present_count / len(result.sections)
    return round(ratio * WEIGHTS["sections"])


def _score_skills(result: AnalysisResult) -> int:
    count = len(result.skills)
    if count == 0:
        result.findings.append(
            Finding("Skills", "bad", "No recognisable technical skills were detected.")
        )
        return 0

    result.findings.append(
        Finding("Skills", "good" if count >= 5 else "warn", f"{count} recognisable skills detected.")
    )

    ratio = min(count / 12, 1.0)
    return round(ratio * WEIGHTS["skills"])


def _score_experience(text: str, result: AnalysisResult) -> int:
    has_experience_heading = result.sections.get("experience", False)
    lowered = text.lower()
    verb_hits = sum(1 for verb in ACTION_VERBS if verb in lowered)

    if has_experience_heading:
        result.findings.append(Finding("Experience", "good", "Experience or internship section present."))
    else:
        result.findings.append(
            Finding(
                "Experience",
                "warn",
                "No experience section. Add internships, freelance or academic projects.",
            )
        )

    if verb_hits >= 5:
        result.findings.append(
            Finding("Experience", "good", f"Strong action verbs used ({verb_hits} distinct).")
        )
    elif verb_hits >= 2:
        result.findings.append(
            Finding("Experience", "warn", "Use more action verbs (built, led, optimized...).")
        )
    else:
        result.findings.append(
            Finding("Experience", "bad", "Almost no action verbs. Start bullets with strong verbs.")
        )

    points = 0
    points += 10 if has_experience_heading else 3
    points += round(min(verb_hits / 8, 1.0) * 10)
    return min(points, WEIGHTS["experience"])


def _score_education(text: str, result: AnalysisResult) -> int:
    has_education = result.sections.get("education", False)
    has_degree = bool(
        re.search(r"\b(b\.?sc|b\.?tech|b\.?e\b|m\.?sc|m\.?tech|mba|bca|mca|bachelor|master|phd|diploma)\b", text, re.IGNORECASE)
    )
    if has_education or has_degree:
        result.findings.append(Finding("Education", "good", "Education details detected."))
        return WEIGHTS["education"]
    result.findings.append(Finding("Education", "warn", "No education/degree details detected."))
    return 0


def _score_impact(text: str, result: AnalysisResult) -> int:
    quantified = len(METRIC_RE.findall(text))
    years = len(set(YEAR_RE.findall(text)))

    if quantified >= 3:
        result.findings.append(
            Finding("Impact", "good", f"{quantified} quantified achievements found. Excellent.")
        )
        points = 10
    elif quantified >= 1:
        result.findings.append(
            Finding("Impact", "warn", "Some numbers used. Quantify more achievements with metrics.")
        )
        points = 6
    else:
        result.findings.append(
            Finding(
                "Impact",
                "bad",
                "No quantified achievements. Add numbers (%, time saved, users, revenue).",
            )
        )
        points = 0

    # Dated entries help ATS parsing.
    if years >= 2:
        result.findings.append(Finding("Impact", "good", "Dated entries found (years present)."))

    return points


def analyse_resume(text: str) -> AnalysisResult:
    """Run the full heuristic analysis and return a structured result."""
    result = AnalysisResult()
    result.word_count = len(text.split())
    result.skills = extract_skills(text)
    result.skills_by_category = categorise_skills(result.skills)
    result.sections = detect_sections(text)

    result.subscores = {
        "contact": _score_contact(text, result),
        "sections": _score_sections(result),
        "skills": _score_skills(result),
        "experience": _score_experience(text, result),
        "education": _score_education(text, result),
        "impact": _score_impact(text, result),
    }

    result.score = max(0, min(100, sum(result.subscores.values())))

    # Word-count sanity check.
    if result.word_count < 150:
        result.findings.append(
            Finding("Length", "warn", f"Only {result.word_count} words. Resumes are usually 300-700 words.")
        )
    elif result.word_count > 1200:
        result.findings.append(
            Finding("Length", "warn", f"{result.word_count} words. Consider trimming to stay concise.")
        )
    else:
        result.findings.append(
            Finding("Length", "good", f"Good length ({result.word_count} words).")
        )

    result.suggestions = _build_suggestions(result)
    return result


def _build_suggestions(result: AnalysisResult) -> list[str]:
    """Turn weak findings into an actionable, prioritised to-do list."""
    suggestions: list[str] = []

    for finding in result.problems:
        suggestions.append(f"[Priority] {finding.message}")
    for finding in result.warnings:
        suggestions.append(finding.message)

    if result.skills:
        suggestions.append(
            "Tailor the skills section to each job advert and mirror its exact wording."
        )
    if not result.sections.get("summary"):
        suggestions.append(
            "Add a 2-3 line professional summary at the top stating your target role."
        )

    if not suggestions:
        suggestions.append("This resume is in great shape. Tailor keywords per application.")

    return suggestions
