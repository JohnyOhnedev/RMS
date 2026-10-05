"""URL routes for the home app."""

from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    # Landing / static pages
    path("", views.home, name="home"),
    path("features/", views.features, name="features"),

    # Candidate authentication (both clean and legacy .html paths supported)
    path("login/", views.login_view, name="login"),
    path("login.html", views.login_view),
    path("signup/", views.signup_view, name="signup"),
    path("signup.html", views.signup_view),
    path("logout/", views.logout_view, name="logout"),
    path("afterlogin/", views.afterlogin_view, name="afterlogin"),

    # Resume features
    path("analyze/", views.process_resume, name="process_resume"),
    path("features/upload.html", views.process_resume, name="upload_resume"),
    path("features/upload_resume.html", views.upload_resume2, name="predict_roles"),
    path("features/upload3.html", views.recommend_resources, name="recommend_resources"),
    path("features/upload4.html", views.process_resume2, name="interview_plan"),
    path("upload-resume/", views.upload_resume_dedup, name="upload_resume_dedup"),

    # Company workspace
    path("company/signup/", views.company_signup, name="company_signup"),
    path("company/login/", views.company_login, name="company_login"),
    path("company-dashboard/", views.company_dashboard, name="company_dashboard"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("fetch-skills/", views.fetch_skills, name="fetch_skills"),

    # Admin review queue
    path("review-queue/", views.review_queue, name="review_queue"),
    path("review-queue/import/", views.import_job_data, name="import_job_data"),
]
