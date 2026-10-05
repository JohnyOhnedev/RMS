"""Job-role prediction: maps resume text to the closest known job roles.

The original project retrained a TF-IDF + NearestNeighbors model on every
upload and mutated a module-level DataFrame loaded at import time. This module
keeps a single cached, lazily-built model that is invalidated whenever the job
dataset changes.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

# Path to the persisted role dataset. Overridable so tests can point at a
# temp file instead of mutating the real project data.
DATA_FILE = Path(settings.BASE_DIR) / "job_data.json"


def set_data_file(path) -> None:
    """Redirect the dataset to another path (used by tests).

    Passing the real path back restores normal behaviour.
    """
    global DATA_FILE
    DATA_FILE = Path(path)
    invalidate_model()


def reset_data_file() -> None:
    """Restore the default dataset path."""
    set_data_file(Path(settings.BASE_DIR) / "job_data.json")

# Seed dataset: role -> space/comma separated core skills.
INITIAL_JOB_DATA: dict[str, str] = {
    "Data Scientist": "machine learning, python, data analysis, statistics, big data, predictive modeling, data visualization, SQL, R, AI frameworks, data wrangling, feature engineering, Hadoop, Spark, business acumen, communication skills, time-series analysis, cloud computing, database management",
    "Software Engineer": "programming, software development, java, python, debugging, software architecture, version control, problem-solving, algorithms, data structures, software testing, REST APIs, microservices, cloud platforms, full-stack development, design patterns, performance optimization, teamwork",
    "Project Manager": "project management, communication, leadership, planning, budgeting, scheduling, risk management, stakeholder management, Agile, Scrum, conflict resolution, resource allocation, change management, team collaboration, negotiation, project scope definition, time management, project tracking tools",
    "Web Developer": "html, css, javascript, web development, responsive design, web performance, React, Angular, frontend frameworks, REST APIs, Vue.js, accessibility standards, cross-browser compatibility, backend integration, Node.js, Bootstrap, GraphQL, web security principles, testing debugging tools",
    "System Administrator": "networking, system management, troubleshooting, linux, server maintenance, scripting, security protocols, virtualization, cloud services, Windows Server, database administration, backup and recovery, IT automation, system monitoring, IT compliance, disaster recovery, DNS, DHCP",
    "UX Designer": "user experience, design thinking, prototyping, wireframing, user research, usability testing, interaction design, visual design, Figma, Adobe XD, accessibility design, UX writing, motion design, design systems, empathy mapping, persona creation, heuristic evaluation, storytelling, cross-functional collaboration",
    "Business Analyst": "data analysis, requirements gathering, problem solving, communication, stakeholder engagement, documentation, process improvement, SQL, visualization tools, business intelligence, financial analysis, Tableau, Power BI, data storytelling, gap analysis, SWOT analysis, system integration, cost-benefit analysis",
    "Cybersecurity Specialist": "cybersecurity, network security, risk assessment, cryptography, ethical hacking, incident response, firewalls, penetration testing, security audits, vulnerability assessment, security frameworks, SIEM tools, compliance standards, forensic analysis, identity management, zero-trust architecture, threat modeling",
    "Cloud Engineer": "cloud computing, aws, azure, cloud architecture, containerization, Kubernetes, cloud security, serverless computing, cost optimization, Terraform, OpenStack, GCP, hybrid cloud solutions, cloud migration, cloud monitoring tools, API integration, DevOps principles, multi-cloud strategies",
    "AI Engineer": "artificial intelligence, deep learning, machine learning, python, neural networks, TensorFlow, PyTorch, NLP, computer vision, AI ethics, reinforcement learning, GANs, transfer learning, edge AI, AI model deployment, MLOps, algorithm optimization, GPU computing, cloud AI services, explainable AI",
    "DevOps Engineer": "devops, ci/cd, automation, containerization, Docker, Kubernetes, cloud platforms, infrastructure as code, monitoring, scripting, Jenkins, Ansible, Terraform, configuration management, system reliability, cloud cost optimization, incident response, system scalability, version control systems, Agile methodologies",
    "Database Administrator": "database management, sql, nosql, data modeling, database security, performance tuning, backup and recovery, Oracle, MySQL, PostgreSQL, MongoDB, database replication, clustering, query optimization, ETL processes, database monitoring, database migration, disaster recovery, schema design, database auditing",
    "Digital Marketing Specialist": "seo, social media, content marketing, google analytics, PPC campaigns, email marketing, keyword research, brand strategy, data analysis, influencer marketing, conversion rate optimization, A/B testing, marketing automation, CRM systems, mobile marketing, copywriting, video marketing, affiliate marketing",
    "Product Manager": "product lifecycle management, roadmap planning, customer research, agile methodologies, UX/UI principles, stakeholder communication, competitive analysis, MVP development, feature prioritization, market research, cross-functional team coordination, data-driven decision-making, product analytics, customer journey mapping, pricing strategies, business strategy",
    "Electrical Engineer": "circuit design, power systems, plc programming, embedded systems, signal processing, renewable energy systems, MATLAB, PCB design, IoT devices, electrical safety, high-voltage systems, power electronics, SCADA systems, control systems, microcontrollers, energy efficiency, project management",
    "Civil Engineer": "construction management, structural analysis, autocad, surveying, project planning, cost estimation, geotechnical engineering, sustainability, building codes, BIM software, construction materials, CAD software, foundation design, hydraulic engineering, urban planning, environmental impact assessment",
    "Content Writer": "copywriting, content creation, seo writing, storytelling, grammar, editing, research, creative writing, content strategy, audience engagement, social media writing, technical writing, blogging, brand voice, proofreading, long-form content, content repurposing, CMS platforms, analytics-driven content",
    "Human Resources Specialist": "recruitment, employee relations, training, hr policies, conflict resolution, performance management, payroll systems, compliance, organizational development, talent acquisition, HRIS systems, benefits administration, employee engagement, diversity and inclusion, labor law knowledge, succession planning, conflict mediation",
    "Graphic Designer": "adobe photoshop, adobe illustrator, typography, branding, color theory, layout design, visual storytelling, print design, digital media, creativity, motion graphics, 3D design, Canva, marketing campaigns, UX/UI design, illustration, photo editing, packaging design, web design principles",
    "Teacher": "teaching, curriculum development, classroom management, communication, lesson planning, student assessment, subject expertise, online teaching tools, mentoring, collaborative learning, differentiated instruction, educational technology, behavior management, parent communication, extracurricular activity planning, lifelong learning strategies, cultural competency",
}

_lock = threading.Lock()
_model_cache: dict = {"signature": None, "vectorizer": None, "model": None, "roles": None}


def load_job_data() -> dict[str, str]:
    """Load and merge the persisted job dataset with the seed dataset."""
    data: dict[str, str] = {}
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Could not read %s: %s", DATA_FILE, exc)

    return {**INITIAL_JOB_DATA, **data}


def save_job_data(data: dict[str, str]) -> None:
    """Persist the job dataset atomically and invalidate the model cache."""
    tmp = DATA_FILE.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=4, sort_keys=True)
    tmp.replace(DATA_FILE)
    invalidate_model()


def _dataset_signature(data: dict[str, str]) -> tuple:
    return tuple(sorted((role, skills) for role, skills in data.items()))


def invalidate_model() -> None:
    """Force the next prediction call to rebuild the model."""
    with _lock:
        _model_cache["signature"] = None


def get_model():
    """Return a cached (vectorizer, model, roles) tuple, rebuilding if stale."""
    data = load_job_data()
    signature = _dataset_signature(data)

    with _lock:
        if _model_cache["signature"] == signature and _model_cache["model"] is not None:
            return _model_cache["vectorizer"], _model_cache["model"], _model_cache["roles"]

        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.neighbors import NearestNeighbors

        roles = list(data.keys())
        corpus = [data[role] for role in roles]

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        matrix = vectorizer.fit_transform(corpus)

        n_neighbors = max(1, min(3, len(roles)))
        model = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
        model.fit(matrix)

        _model_cache.update(
            {"signature": signature, "vectorizer": vectorizer, "model": model, "roles": roles}
        )
        logger.info("Job-role model built for %d roles", len(roles))
        return vectorizer, model, roles


def predict_job_roles(resume_text: str, top_n: int = 3) -> list[tuple[str, float]]:
    """Return the ``top_n`` best-matching job roles with a 0-100 score."""
    if not resume_text or not resume_text.strip():
        return []

    vectorizer, model, roles = get_model()
    vector = vectorizer.transform([resume_text])

    n = max(1, min(top_n, len(roles)))
    distances, indices = model.kneighbors(vector, n_neighbors=n)

    predictions: list[tuple[str, float]] = []
    for distance, index in zip(distances[0], indices[0]):
        cosine_similarity = max(0.0, 1.0 - float(distance))
        predictions.append((roles[index], round(cosine_similarity * 100, 2)))
    return predictions


def add_or_update_role(job_role: str, skills: str) -> str:
    """Add a job role or merge new skills into an existing one.

    Returns a short human-readable status message.
    """
    job_role = (job_role or "").strip()
    skills = (skills or "").strip()
    if not job_role or not skills:
        raise ValueError("Both a job role and at least one skill are required.")

    data = load_job_data()
    incoming = {
        skill.strip().lower() for skill in skills.replace(";", ",").split(",") if skill.strip()
    }

    existing_role = next(
        (role for role in data if role.casefold() == job_role.casefold()), None
    )

    if existing_role:
        current = {
            skill.strip().lower()
            for skill in data[existing_role].replace(";", ",").split(",")
            if skill.strip()
        }
        merged = current | incoming
        data[existing_role] = ", ".join(sorted(merged))
        message = f"Updated skills for '{existing_role}'."
    else:
        canonical = job_role.title()
        data[canonical] = ", ".join(sorted(incoming))
        message = f"Added new job role '{canonical}'."

    save_job_data(data)
    return message


def get_skills_for_role(job_role: str) -> str:
    """Case-insensitive lookup of the skills registered for a job role."""
    job_role = (job_role or "").strip()
    if not job_role:
        return ""
    data = load_job_data()
    existing_role = next(
        (role for role in data if role.casefold() == job_role.casefold()), None
    )
    return data.get(existing_role, "") if existing_role else ""
