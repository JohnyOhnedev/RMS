"""Test suite for the RMS application.

Run with:  python manage.py test
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from home.models import Company, ResumeEntry, UserResume
from home.services import job_predictor
from home.services.exceptions import EmptyResumeError, UnsupportedFileType
from home.services.resume_analyzer import analyse_resume
from home.services.resume_parser import extract_text, normalise_text
from home.services.skill_extractor import extract_skills, detect_sections

SAMPLE_RESUME = """John Doe
Software Developer
john.doe@example.com | +91 98765 43210 | linkedin.com/in/johndoe | github.com/johndoe

SUMMARY
Backend developer with 3 years of experience building scalable web services.

EXPERIENCE
Software Engineer, Acme Corp (2022 - Present)
- Built a Django REST API serving 50,000 requests per day, reducing latency by 35%
- Led migration of 12 legacy endpoints to PostgreSQL, cutting query time by 60%
- Implemented CI/CD pipelines with Docker and GitHub Actions

EDUCATION
B.Tech Computer Science, Government Engineering College, 2018 - 2022

SKILLS
Python, Django, PostgreSQL, Docker, AWS, Git, REST API, Redis, Linux

PROJECTS
Inventory Tracker - Flask app with 200+ active users
- Automated stock reconciliation, saving 10 hours per week

CERTIFICATIONS
AWS Certified Cloud Practitioner (2023)
"""


class SkillExtractionTests(TestCase):
    def test_extracts_known_skills(self):
        skills = extract_skills(SAMPLE_RESUME)
        for expected in ("python", "django", "postgresql", "docker", "aws"):
            self.assertIn(expected, skills)

    def test_case_insensitive(self):
        self.assertIn("python", extract_skills("PYTHON and Java"))

    def test_detects_sections(self):
        sections = detect_sections(SAMPLE_RESUME)
        self.assertTrue(sections["education"])
        self.assertTrue(sections["skills"])
        self.assertTrue(sections["experience"])

    def test_letter_spaced_headings(self):
        text = "E D U C A T I O N\nBSc Computer Science\n\nS K I L L S\nPython"
        sections = detect_sections(text)
        self.assertTrue(sections["education"])
        self.assertTrue(sections["skills"])

    def test_empty_text(self):
        self.assertEqual(extract_skills(""), [])


class ResumeAnalyzerTests(TestCase):
    def test_score_in_range(self):
        result = analyse_resume(SAMPLE_RESUME)
        self.assertGreaterEqual(result.score, 0)
        self.assertLessEqual(result.score, 100)
        self.assertEqual(sum(result.subscores.values()), result.score)

    def test_strong_resume_scores_well(self):
        result = analyse_resume(SAMPLE_RESUME)
        self.assertGreater(result.score, 60, f"Expected >60, got {result.score}")

    def test_weak_resume_scores_low(self):
        result = analyse_resume("hi")
        self.assertLess(result.score, 45)

    def test_finds_quantified_impact(self):
        result = analyse_resume(SAMPLE_RESUME)
        self.assertEqual(result.subscores["impact"], 10)

    def test_provides_suggestions(self):
        result = analyse_resume("Just a name")
        self.assertTrue(result.suggestions)

    def test_grade_labels(self):
        self.assertIn(analyse_resume(SAMPLE_RESUME).grade, {"Excellent", "Good", "Fair", "Needs work"})


class ResumeParserTests(TestCase):
    def test_plain_text_upload(self):
        upload = SimpleUploadedFile("c.txt", b"Hello resume world", content_type="text/plain")
        self.assertEqual(extract_text(upload), "Hello resume world")

    def test_unsupported_extension(self):
        upload = SimpleUploadedFile("bad.exe", b"\x00\x01", content_type="application/octet-stream")
        with self.assertRaises(UnsupportedFileType):
            extract_text(upload)

    def test_empty_file_raises(self):
        upload = SimpleUploadedFile("empty.txt", b"   \n  ", content_type="text/plain")
        with self.assertRaises(EmptyResumeError):
            extract_text(upload)

    def test_normalise_text(self):
        self.assertEqual(normalise_text("a\x00b\n\n\n c  "), "ab\nc")


class JobPredictorTests(TestCase):
    """Job-role tests run against an isolated temp dataset.

    ``add_or_update_role`` writes to disk, so pointing at the real
    ``job_data.json`` would mutate the user's data. Each test gets a throwaway
    file seeded from INITIAL_JOB_DATA and the original path is restored after.
    """

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._data_file = Path(self._tmpdir.name) / "job_data.json"
        self._data_file.write_text(json.dumps(job_predictor.INITIAL_JOB_DATA), encoding="utf-8")
        job_predictor.set_data_file(self._data_file)

    def tearDown(self):
        job_predictor.reset_data_file()
        self._tmpdir.cleanup()

    def test_predictions_ranked(self):
        preds = job_predictor.predict_job_roles(SAMPLE_RESUME)
        self.assertTrue(preds)
        scores = [score for _, score in preds]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_empty_text_returns_nothing(self):
        self.assertEqual(job_predictor.predict_job_roles(""), [])

    def test_add_role_and_lookup(self):
        message = job_predictor.add_or_update_role("Test Role", "python, django")
        self.assertIn("Added", message)
        self.assertIn("python", job_predictor.get_skills_for_role("test role"))

    def test_merge_existing_role(self):
        job_predictor.add_or_update_role("Merge Role", "python")
        job_predictor.add_or_update_role("Merge Role", "django")
        skills = job_predictor.get_skills_for_role("Merge Role")
        self.assertIn("python", skills)
        self.assertIn("django", skills)

    def test_missing_fields_raise(self):
        with self.assertRaises(ValueError):
            job_predictor.add_or_update_role("", "")

    def test_saving_does_not_touch_the_real_dataset(self):
        """Guard: the test suite must never rewrite the project's job_data.json."""
        real = Path(settings.BASE_DIR) / "job_data.json"
        before = real.read_text(encoding="utf-8")
        job_predictor.add_or_update_role("Scratch Role", "python")
        self.assertEqual(real.read_text(encoding="utf-8"), before)


class PublicPageTests(TestCase):
    def test_public_pages_render(self):
        for name in ("home:home", "home:features", "home:login", "home:signup",
                     "home:company_login", "home:company_signup",
                     "home:process_resume", "home:predict_roles",
                     "home:recommend_resources", "home:interview_plan",
                     "home:upload_resume_dedup"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200, f"{name} returned {response.status_code}")

    def test_review_queue_requires_admin(self):
        response = self.client.get(reverse("home:review_queue"))
        self.assertEqual(response.status_code, 302)


class AuthFlowTests(TestCase):
    def test_signup_logs_user_in(self):
        response = self.client.post(
            reverse("home:signup"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "Str0ngPass!23",
                "password_confirmation": "Str0ngPass!23",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="alice").exists())

    def test_signup_password_mismatch(self):
        response = self.client.post(
            reverse("home:signup"),
            {
                "username": "bob",
                "email": "bob@example.com",
                "password": "Str0ngPass!23",
                "password_confirmation": "Different!23",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="bob").exists())

    def test_login_and_logout(self):
        User.objects.create_user("carol", password="Str0ngPass!23")
        response = self.client.post(
            reverse("home:login"), {"username": "carol", "password": "Str0ngPass!23"}
        )
        self.assertRedirects(response, reverse("home:afterlogin"))
        self.client.get(reverse("home:logout"))
        response = self.client.get(reverse("home:afterlogin"))
        self.assertEqual(response.status_code, 302)


class CompanyFlowTests(TestCase):
    def test_company_signup_creates_pending_record(self):
        response = self.client.post(
            reverse("home:company_signup"),
            {
                "company_name": "Acme Ltd",
                "username": "acme",
                "email": "hr@acme.test",
                "password": "Str0ngPass!23",
                "password_confirmation": "Str0ngPass!23",
            },
        )
        self.assertEqual(response.status_code, 200)
        company = Company.objects.get(name="Acme Ltd")
        self.assertEqual(company.approval_status, "pending")

    def test_pending_company_cannot_log_in(self):
        user = User.objects.create_user("pendingco", password="Str0ngPass!23")
        Company.objects.create(user=user, name="Pending Co", approval_status="pending")
        response = self.client.post(
            reverse("home:company_login"),
            {"username": "pendingco", "password": "Str0ngPass!23"},
        )
        self.assertContains(response, "awaiting approval")

    def test_approved_company_logs_in(self):
        user = User.objects.create_user("okco", password="Str0ngPass!23")
        Company.objects.create(user=user, name="OK Co", approval_status="approved")
        response = self.client.post(
            reverse("home:company_login"), {"username": "okco", "password": "Str0ngPass!23"}
        )
        self.assertRedirects(response, reverse("home:company_dashboard"))

    def test_admin_can_approve_from_queue(self):
        admin = User.objects.create_superuser("root", "root@test.io", "Str0ngPass!23")
        user = User.objects.create_user("newco", password="Str0ngPass!23")
        company = Company.objects.create(user=user, name="New Co", approval_status="pending")

        self.client.force_login(admin)
        response = self.client.post(
            reverse("home:review_queue"), {f"company_{company.id}": "approve"}
        )
        self.assertEqual(response.status_code, 302)
        company.refresh_from_db()
        self.assertEqual(company.approval_status, "approved")


class ResumeUploadViewTests(TestCase):
    """Upload tests.

    Model rows are rolled back by the test transaction, but files written to
    MEDIA_ROOT are NOT, so tearDown removes anything this class created.
    """

    def setUp(self):
        self._upload_dir = Path(settings.MEDIA_ROOT) / "resumes"
        self._before = set(self._upload_dir.iterdir()) if self._upload_dir.is_dir() else set()

    def tearDown(self):
        if not self._upload_dir.is_dir():
            return
        for path in self._upload_dir.iterdir():
            if path not in self._before and path.is_file():
                try:
                    path.unlink()
                except OSError:
                    pass

    def _upload(self, url_name, filename="resume.txt", content=SAMPLE_RESUME.encode()):
        upload = SimpleUploadedFile(filename, content, content_type="text/plain")
        return self.client.post(reverse(url_name), {"resume": upload})

    def test_analysis_view_creates_record(self):
        response = self._upload("home:process_resume")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserResume.objects.count(), 1)
        self.assertContains(response, "/100")

    def test_job_match_view(self):
        response = self._upload("home:predict_roles")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Job role")

    def test_resources_view(self):
        response = self._upload("home:recommend_resources")
        self.assertEqual(response.status_code, 200)

    def test_interview_plan_view(self):
        response = self._upload("home:interview_plan")
        self.assertEqual(response.status_code, 200)

    def test_rejects_unsupported_type(self):
        upload = SimpleUploadedFile("evil.exe", b"MZ\x00", content_type="application/octet-stream")
        response = self.client.post(reverse("home:process_resume"), {"resume": upload})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserResume.objects.count(), 0)

    def test_dedup_blocks_second_upload(self):
        payload = b"unique resume content"
        first = SimpleUploadedFile("a.txt", payload, content_type="text/plain")
        response = self.client.post(reverse("home:upload_resume_dedup"), {"resume": first})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ResumeEntry.objects.count(), 1)

        second = SimpleUploadedFile("a.txt", payload, content_type="text/plain")
        response = self.client.post(reverse("home:upload_resume_dedup"), {"resume": second})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(ResumeEntry.objects.count(), 1)

    def test_dedup_stores_exactly_one_file_on_disk(self):
        """Regression guard for the bug that filled media/ with 190 copies.

        The legacy project saved a new file for every upload, so 10 distinct
        documents ended up as 190 files. Uploading the same bytes repeatedly
        must add exactly one file to MEDIA_ROOT/resumes.
        """
        import os

        from django.conf import settings

        upload_dir = os.path.join(settings.MEDIA_ROOT, "resumes")
        before = len(os.listdir(upload_dir)) if os.path.isdir(upload_dir) else 0

        payload = b"identical bytes uploaded three times"
        for index in range(3):
            upload = SimpleUploadedFile(f"dup_{index}.txt", payload, content_type="text/plain")
            self.client.post(reverse("home:upload_resume_dedup"), {"resume": upload})

        after = len(os.listdir(upload_dir))
        self.assertEqual(ResumeEntry.objects.count(), 1)
        self.assertEqual(after - before, 1, "dedup must store the file exactly once")

        # Remove the file this test created so the media tree stays clean.
        entry = ResumeEntry.objects.first()
        if entry and entry.uploaded_file and os.path.exists(entry.uploaded_file.path):
            os.remove(entry.uploaded_file.path)


class FetchSkillsTests(TestCase):
    def test_returns_skills_json(self):
        response = self.client.get(reverse("home:fetch_skills"), {"job_role": "Data Scientist"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("machine learning", response.json()["skills"])

    def test_unknown_role_returns_empty(self):
        response = self.client.get(reverse("home:fetch_skills"), {"job_role": "Nonsense Role"})
        self.assertEqual(response.json()["skills"], "")
