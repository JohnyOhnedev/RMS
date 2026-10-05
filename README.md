# RMS — Resume Management System

A Django web application that helps candidates improve their resumes and helps
companies match them to job roles. Originally a degree project, this version has
been rebuilt to run out of the box on modern Python with current dependency
versions and a proper service layer.

---

## What it does

| Feature | Description |
|---|---|
| **ATS resume review** | Scores a resume 0–100 across contact details, structure, skills, experience, education and quantified impact, with a prioritised action list. |
| **Job-role matching** | Ranks the resume against 60+ job-role skill profiles using TF-IDF cosine similarity. |
| **Learning resources** | Detects the resume's field(s) and recommends curated courses (Data Science, Web, Mobile, UI/UX). |
| **Interview plans** | Generates a tailored interview plan (technical, behavioural, culture-fit questions). |
| **Company workspace** | Companies register (subject to admin approval), define job roles and required skills. |
| **Admin review queue** | Administrators approve or reject company registrations; approved companies receive an email. |
| **Duplicate detection** | SHA-256 hashing prevents the same resume being uploaded twice. |
| **Animated UI** | Glassmorphic surfaces, an ambient aurora background, scroll-reveal, count-up scores, animated progress bars, and card tilt — all progressive enhancement. |

Everything works **fully offline**. AI features (Google Gemini) are optional and
the app falls back to a deterministic local analyser when no API key is set.

---

## Quick start

```bash
cd rms

# 1. Create and activate a virtual environment (Python 3.10–3.12)
uv venv --python 3.12 .venv      # or: python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
uv pip install -r requirements.txt   # or: pip install -r requirements.txt

# 3. Create your environment file
cp .env.example .env
#    then edit .env — at minimum set DJANGO_SECRET_KEY

# 4. Set up the database
python manage.py migrate

# 5. Create an administrator account
python manage.py createsuperuser

# 6. Run it
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

The admin dashboard is at <http://127.0.0.1:8000/admin/> and the company
approval queue at <http://127.0.0.1:8000/review-queue/>.

---

## Configuration

All configuration lives in `.env` (see `.env.example`). The important ones:

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | dev placeholder | **Set a real value in production.** |
| `DJANGO_DEBUG` | `True` | Set `False` in production. |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma separated. |
| `DB_ENGINE` | `sqlite` | Set to `mysql` to use MySQL (see `DB_*` vars). |
| `GEMINI_API_KEY` | empty | Optional. Enables AI review / interview plans. |
| `DJANGO_EMAIL_BACKEND` | console | Switch to the SMTP backend to send real email. |
| `MAX_RESUME_UPLOAD_SIZE` | `8388608` (8 MB) | Upload size limit in bytes. |

### Enabling AI features

Get a key from <https://aistudio.google.com/app/apikey>, then set in `.env`:

```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.0-flash
```

Model names are configurable because Google retires them regularly — update
`GEMINI_MODEL` if you see a "model not found" error. Without a key the app uses
its built-in offline analyser, so nothing breaks.

### Using MySQL instead of SQLite

```
DB_ENGINE=mysql
DB_NAME=rms
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

```bash
pip install mysqlclient   # required for MySQL
python manage.py migrate
```

---

## Project layout

```
rms/
├── manage.py
├── requirements.txt
├── .env.example
├── job_data.json              # job role -> required skills dataset
├── home/
│   ├── models.py              # UserResume, Company, ResumeEntry
│   ├── forms.py               # signup / upload forms with validation
│   ├── urls.py                # app routes
│   ├── admin.py               # admin with approve/reject bulk actions
│   ├── context_processors.py
│   ├── utils.py               # email + legacy parsing helpers
│   ├── views/
│   │   ├── auth_views.py      # login, signup, logout, landing
│   │   ├── resume_views.py    # upload, analysis, matching, resources
│   │   └── company_views.py   # company auth, dashboard, review queue
│   ├── services/
│   │   ├── resume_parser.py   # PDF / DOCX / TXT / OCR extraction
│   │   ├── resume_analyzer.py # offline ATS scoring
│   │   ├── skill_extractor.py # categorised skill taxonomy
│   │   ├── job_predictor.py   # cached TF-IDF + kNN model
│   │   ├── recommender.py     # course recommendations
│   │   ├── ai_service.py      # Gemini integration + offline fallback
│   │   └── helpers.py
│   ├── templates/             # base.html + one template per page
│   ├── static/
│   │   ├── app.css            # all styling: tokens, glass, animations
│   │   └── app.js             # animation layer (scroll reveal, count-up, tilt)
│   └── tests.py               # 39 tests
├── rms/
│   ├── settings.py            # env-driven configuration
│   └── urls.py
├── tools/
│   └── dedupe_media.py        # collapse duplicate uploads (dry run by default)
└── media/                     # uploaded resumes
```

---

## Running the tests

```bash
python manage.py test
```

39 tests cover skill extraction, ATS scoring, file parsing, job prediction,
authentication, the company approval workflow, duplicate detection and every
upload endpoint.

The suite is **self-cleaning and idempotent**: it runs against a temporary copy
of the job dataset and removes any files it writes to `media/`, so repeated runs
leave `job_data.json` and `media/` byte-for-byte unchanged. Verify with:

```bash
md5sum job_data.json && find media/ -type f | wc -l
python manage.py test && python manage.py test
md5sum job_data.json && find media/ -type f | wc -l   # must be identical
```

```bash
python manage.py test -v 2                      # verbose
python manage.py test home.tests.ResumeAnalyzerTests   # one class
```

---

## Main routes

| URL | Purpose |
|---|---|
| `/` | Landing page with quick analysis |
| `/features/` | Feature overview |
| `/login/`, `/signup/` | Candidate authentication |
| `/afterlogin/` | Candidate dashboard |
| `/analyze/` | ATS resume review |
| `/features/upload_resume.html` | Job-role matching |
| `/features/upload3.html` | Learning resources |
| `/features/upload4.html` | Interview plan |
| `/upload-resume/` | Upload with duplicate detection |
| `/company/signup/`, `/company/login/` | Company authentication |
| `/company-dashboard/` | Manage roles and skills |
| `/review-queue/` | Admin company approval queue |
| `/fetch-skills/` | JSON API for role skills |
| `/admin/` | Django admin |

---

## Notes on the modernisation

Changes made from the original degree-project version:

**It runs at all**
- Replaced hard-coded MySQL credentials with SQLite by default; MySQL is opt-in.
- Removed the hard-coded, leaked Gmail password and API key from source — both
  are now environment variables.
- Fixed the `urls.py` file, which defined `urlpatterns` four times (the first
  three definitions were silently discarded) and pointed several routes at the
  wrong views.
- Fixed duplicate URL names that made `{% url %}` raise `NoReverseMatch`.
- Added the missing `review_queue.html` route integration and corrected the
  view decorators that had been split by a stacked-comment bug.

**It is maintainable**
- Split the 1,399-line `views.py` into `auth_views`, `resume_views` and
  `company_views`, with all domain logic moved into `services/`.
- Removed the import-time model training that rewrote `job_data.json` on every
  Django start, replacing it with a lazily-built, thread-safe, cached model.
- Consolidated three duplicated copies of the same `DATA_FILE`/`data`/`save_data`
  blocks.
- Removed ~600 lines of dead commented-out code.
- Added a shared `base.html` and rewrote every template to extend it.

**It is more capable**
- New offline ATS scoring engine with per-section subscores.
- New categorised skill taxonomy (10 categories, 150+ skills) replacing a
  30-item flat keyword list.
- Letter-spaced PDF headings ("E D U C A T I O N") are now recognised.
- Multi-field course recommendations instead of first-match-wins.
- Structured, actionable fallback output when the AI is unavailable.

**It is safer**
- File type, extension and size validation on all uploads.
- Django password validators enforced on signup.
- Email failures no longer break the approval flow.
- Rotating log files instead of unbounded `django.log` / `error.log` growth
  (the originals had grown to 159 MB and 113 MB).
- Production security settings (HSTS, secure cookies, nosniff) engage
  automatically when `DEBUG=False`.
- Added a working test suite that cannot corrupt your data (see below).

**Duplicate uploads (a real bug that had already bitten this project)**

`media/` shipped with **190 PDF files containing only 10 distinct documents** —
one resume had been stored 68 times, wasting ~20 MB. The `ResumeEntry` model with
its SHA-256 hash column had been written to prevent exactly this, but was never
wired to a URL, so every upload saved a fresh file. Two fixes:

- the dedup endpoint is now live at `/upload-resume/`, with a regression test
  asserting that uploading identical bytes three times writes exactly one file
- the existing backlog was collapsed 190 → 10 files with
  `python tools/dedupe_media.py` (dry run by default; `--apply` to delete)

The dedupe tool groups by SHA-256 of file *content*, keeps the cleanest filename
per group, verifies every file it plans to delete is byte-identical to its
keeper, and refuses to delete anything if a check fails. A `tar.gz` backup of the
full media tree is written before any change. **Take a backup first:**

```bash
tar czf ~/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
python tools/dedupe_media.py            # review the plan
python tools/dedupe_media.py --apply    # delete duplicates
```

`media/` is gitignored, so these files are not tracked by git — the tarball is
your only undo.


**Why the tests can't damage your data**

The first version of the test suite rewrote `job_data.json` on every run and
would have deleted roles that weren't in the built-in seed list (it removed
`Architect` and `Interior Designer` before this was caught). Now:

- job-role tests run against a temp copy of the dataset via
  `job_predictor.set_data_file()`; the real file is never opened for writing
- upload tests delete any files they create, since Django's test transaction
  rolls back DB rows but **not** filesystem writes
- `test_saving_does_not_touch_the_real_dataset` fails loudly if that ever breaks
