"""Skills taxonomy and extraction.

Replaces the hard-coded 30-entry keyword list that lived in views.py with a
broader, categorised taxonomy used by the ATS scorer and the resource recommender.
"""

from __future__ import annotations

import re

# Categorised skill taxonomy: category -> tuple of canonical skill names.
SKILL_TAXONOMY: dict[str, tuple[str, ...]] = {
    "Data Science": (
        "machine learning", "deep learning", "tensorflow", "keras", "pytorch",
        "scikit-learn", "sklearn", "pandas", "numpy", "matplotlib", "seaborn",
        "data analysis", "data science", "statistics", "nlp",
        "natural language processing", "computer vision", "streamlit",
    ),
    "Web Development": (
        "html", "css", "javascript", "typescript", "react", "reactjs",
        "angular", "vue", "node.js", "nodejs", "express", "django", "flask",
        "fastapi", "php", "laravel", "wordpress", "bootstrap", "tailwind",
        "graphql", "rest api", "jquery",
    ),
    "Mobile Development": (
        "android", "kotlin", "flutter", "dart", "swift", "ios", "react native",
        "xamarin", "objective-c",
    ),
    "UI/UX Design": (
        "figma", "adobe xd", "sketch", "zeplin", "balsamiq", "wireframes",
        "prototyping", "user research", "usability testing", "ux", "ui design",
        "interaction design", "invision",
    ),
    "Design & Media": (
        "photoshop", "illustrator", "indesign", "after effects", "premiere pro",
        "canva", "blender", "figma", "typography", "graphic design",
    ),
    "Databases": (
        "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis",
        "nosql", "database design", "query optimization",
    ),
    "Cloud & DevOps": (
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "ci/cd", "devops", "linux",
        "bash", "shell scripting", "git", "github actions", "nginx",
    ),
    "Programming Languages": (
        "python", "java", "c", "c++", "c#", "go", "golang", "rust", "ruby",
        "php", "javascript", "kotlin", "swift", "r", "matlab", "scala", "perl",
    ),
    "Cybersecurity": (
        "network security", "penetration testing", "ethical hacking",
        "cryptography", "siem", "firewalls", "vulnerability assessment",
        "incident response", "owasp", "kali linux", "wireshark",
    ),
    "Office & General": (
        "microsoft office", "excel", "word", "powerpoint", "google sheets",
        "communication", "leadership", "teamwork", "problem solving",
        "project management", "agile", "scrum", "english", "writing",
        "presentation", "time management", "customer service", "public speaking",
        "critical thinking", "adaptability",
    ),
}

# Flat lookups built once at import time.
ALL_SKILLS: tuple[str, ...] = tuple(
    sorted({skill for skills in SKILL_TAXONOMY.values() for skill in skills})
)
SKILL_TO_CATEGORY: dict[str, str] = {
    skill: category for category, skills in SKILL_TAXONOMY.items() for skill in skills
}

# Pre-compile word-boundary patterns for performance.
_SKILL_PATTERNS: dict[str, re.Pattern] = {
    skill: re.compile(r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])", re.IGNORECASE)
    for skill in ALL_SKILLS
}

# Split a resume into rough sections by common headings.
SECTION_HEADINGS = {
    "summary": ("summary", "profile", "objective", "about me", "professional summary"),
    "experience": (
        "experience", "work experience", "employment", "professional experience",
        "internship", "internships",
    ),
    "education": ("education", "academic", "qualification", "qualifications"),
    "skills": ("skills", "technical skills", "core competencies", "technologies"),
    "projects": ("projects", "personal projects", "academic projects"),
    "certifications": ("certifications", "certificates", "courses", "training"),
}


def extract_skills(text: str) -> list[str]:
    """Return canonical skills found in ``text`` (case-insensitive, de-duplicated)."""
    if not text:
        return []

    haystack = text.lower()
    found = [skill for skill, pattern in _SKILL_PATTERNS.items() if pattern.search(haystack)]
    # Prefer the longest label when several overlap (e.g. "react native" vs "react").
    found.sort(key=len, reverse=True)
    deduped: list[str] = []
    for skill in found:
        if not any(skill != other and skill in other for other in deduped):
            deduped.append(skill)
    return sorted(deduped)


def categorise_skills(skills: list[str]) -> dict[str, list[str]]:
    """Group a skill list by category."""
    grouped: dict[str, list[str]] = {}
    for skill in skills:
        category = SKILL_TO_CATEGORY.get(skill, "Other")
        grouped.setdefault(category, []).append(skill)
    return grouped


def _collapse_letter_spacing(text: str) -> str:
    """Turn letter-spaced headings into normal words.

    Many PDF resumes render headings as "E D U C A T I O N" (each letter
    separated by spaces). Collapsing runs of single characters that are
    separated by a single space restores "EDUCATION" so section detection works.
    """
    # A sequence of >=3 single alphanumerics each separated by a single space.
    pattern = re.compile(r"(?:(?<=\s)|^)(?:[A-Za-z0-9]\s){2,}[A-Za-z0-9](?=\s|$)")

    def _join(match: re.Match) -> str:
        return match.group(0).replace(" ", "")

    return pattern.sub(_join, text)


def detect_sections(text: str) -> dict[str, bool]:
    """Detect which standard resume sections are present."""
    lowered = _collapse_letter_spacing(text).lower()
    sections: dict[str, bool] = {}
    for section, headings in SECTION_HEADINGS.items():
        sections[section] = any(
            re.search(rf"(?m)^\s*{re.escape(heading)}\b", lowered) for heading in headings
        )
    return sections
