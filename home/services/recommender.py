"""Course/resource recommendation based on detected resume skills.

Replaces the chain of ``break``-ing if/elif branches in views.py (which only
ever recommended resources for the *first* matched skill) with a scored,
multi-category recommender backed by courses.py.
"""

from __future__ import annotations

from home import courses

from .skill_extractor import SKILL_TAXONOMY, extract_skills

# Map each resume-skill category to the course list that best serves it.
CATEGORY_COURSES = {
    "Data Science": courses.ds_course,
    "Web Development": courses.web_course,
    "Mobile Development": None,  # split below
    "UI/UX Design": courses.uiux_course,
    "Design & Media": courses.uiux_course,
    "Cloud & DevOps": courses.web_course,
    "Cybersecurity": courses.ds_course,
    "Databases": courses.ds_course,
}


def _available(name: str):
    return getattr(courses, name, None) or []


def recommend_resources(resume_text: str, limit_per_field: int = 4) -> dict:
    """Return recommended fields and courses for the given resume text.

    Returns a dict shaped for the ``resources.html`` template::

        {
            "reco_field": "Web Development",
            "fields": ["Web Development", ...],
            "resources": {"Web Development Courses": [[title, url], ...], ...},
            "skills": [...],
        }
    """
    skills = extract_skills(resume_text)

    # Score every taxonomy category by how many of its skills appear.
    category_scores: dict[str, int] = {}
    for skill in skills:
        for category, category_skills in SKILL_TAXONOMY.items():
            if skill in category_skills:
                category_scores[category] = category_scores.get(category, 0) + 1

    if not category_scores:
        return {
            "reco_field": "General",
            "fields": [],
            "resources": {
                "General": [["No specific field detected - add more technical skills to your resume.", ""]]
            },
            "skills": skills,
        }

    # Rank categories, keeping only those with a real signal.
    ranked = sorted(category_scores.items(), key=lambda item: (-item[1], item[0]))
    top_fields = [category for category, score in ranked[:3] if score > 0]

    resources: dict[str, list[list[str]]] = {}
    for field in top_fields:
        course_list: list[list[str]] = []

        if field == "Mobile Development":
            course_list = _available("android_course") + _available("ios_course")
        else:
            course_list = list(CATEGORY_COURSES.get(field) or [])

        if not course_list:
            course_list = _available("web_course") + _available("ds_course")

        resources[f"{field} Courses"] = course_list[:limit_per_field]

    return {
        "reco_field": top_fields[0],
        "fields": top_fields,
        "resources": resources,
        "skills": skills,
    }
