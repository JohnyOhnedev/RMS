# GitHub repo text for RMS

## About / description (paste into the repo header)

GitHub's "Description" field allows **350 characters**. All options below are
verified to fit.

**Recommended (162 chars):**

```
AI-assisted resume screening platform built with Django. ATS scoring, job-role matching and course recommendations. Fully offline, with optional Google Gemini AI.
```

**Alternative (164 chars):**

```
Django resume screening platform with ATS-style scoring, TF-IDF job-role matching and skill-gap recommendations. Runs fully offline, with optional Google Gemini AI.
```

**Longer, if you want more detail (257 chars):**

```
AI-assisted resume screening platform built with Django. Scores resumes with an ATS-style analyser, matches candidates to job roles using TF-IDF similarity, and recommends learning resources — with an optional Google Gemini layer and full offline operation.
```

---

## Topics (the tag chips under the description)

```
django
django-application
resume
resume-parser
resume-screening
ats
ats-resume
applicant-tracking-system
nlp
tf-idf
scikit-learn
machine-learning
pdf-parsing
docx
gemini
google-gemini
python
python3
sqlite
web-application
```

Pick 10-20; GitHub allows up to 20. The first ten above are the most useful for
discoverability.

---

## README intro block

Drop this at the top of README.md, under the title.

> **RMS (Resume Management System)** is a Django web application that helps
> candidates improve their resumes and helps recruiters find the right people.
>
> Candidates upload a resume (PDF, DOCX or TXT) and get an instant ATS score out
> of 100, a section-by-section breakdown, a prioritised list of fixes, ranked
> job-role matches, and curated courses for the skills they're missing.
> Companies register, define job roles with required skills, and candidates are
> matched against that live data.
>
> Everything runs **fully offline** out of the box — the scoring engine, skill
> extraction and job matching are all local. Adding a Google Gemini API key
> layers on AI-written resume reviews and tailored interview plans, and the app
> degrades gracefully to the local analyser when no key is configured.

---

## What makes it worth a look (feature bullets for the README)

- **ATS scoring engine** — 0-100 across six weighted dimensions (contact,
  structure, skills, experience, education, quantified impact) with actionable
  feedback, not just a number.
- **Semantic job matching** — TF-IDF + cosine similarity against 60+ job-role
  skill profiles, with a cached model that retrains when the dataset changes.
- **Broad skill taxonomy** — 150+ skills across 10 categories, with
  case-insensitive matching and category-level reporting.
- **Real PDF parsing** — handles letter-spaced headings (`E D U C A T I O N`)
  that defeat naive text extraction, plus DOCX (paragraphs *and* tables) and
  optional OCR for scanned resumes.
- **AI optional, never required** — Google Gemini integration behind a
  configurable model name, with a deterministic offline fallback so no feature
  is gated behind an API key.
- **Company workflow** — registration, admin approval queue with email
  notification, and a self-service dashboard for managing roles and skills.
- **Duplicate detection** — SHA-256 content hashing plus a CLI tool to
  de-duplicate an existing upload backlog.

---

## Built with

Django · Python 3.12 · scikit-learn · pandas · PyMuPDF · pypdf · python-docx ·
Pillow · chardet · Google Gemini (optional) · SQLite (MySQL supported)
