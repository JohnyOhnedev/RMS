# # home/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
    
#     path('',views.home,name='home'),
#     path('login/', views.login_view, name='login'),
    
#     path('login.html', views.login_view, name='login'),
#     path('signup.html', views.signup_view, name='signup'),
#     path('signup/', views.signup_view, name='signup'),
#     # path('afterlogin/', views.afterlogin_view, name='afterlogin_view'),
#     # path('afterlogin.html', views.afterlogin_view, name='afterlogin_view'),
    

    
    
    
    
# ]
# from django.urls import path
# from .views import analyze_resume_home

# urlpatterns = [
#     path('', analyze_resume_home, name='home'),
# ]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),  # Ensure `views.home` is defined
# ]


from django.urls import path
from . import views  # Import views from the app

urlpatterns = [
    path('upload/', views.process_resume, name='process_resume'), # For uploading resumes
]
from django.urls import path
from .views import upload_resume2

urlpatterns = [
    # path('', views.home, name='home'),  # Home page URL pattern
    # path('features/', views.features, name='features'),
    # path('features/upload_resume.html', upload_resume2, name='upload_resume'),
    path('', views.home, name='home'),
    path('login.html', views.login_view, name='login'),
    path('dashboard/login.html', views.login_view, name='login'),
    path('signup.html', views.signup_view, name='signup'),
    path('dashboard/signup.html', views.signup_view, name='signup'),
    path('afterlogin/', views.afterlogin_view, name='afterlogin'),
    path('features/', views.features, name='features'),
    path('features/upload.html', views.process_resume, name='upload_resume'),
    path('features/upload_resume.html', views.upload_resume2, name='upload_resume'),
    #path('features/upload3.html', views.recommend_resources, name='recommend_resources'),   # Add this line
    path('features/upload4.html', views.process_resume2, name='upload_resume3'),
    #path('features/view_resumes.html', views.view_resumes_inline, name='view_resumes'),
    #path('upload_resume/', views.upload_resume5, name='upload_resume5'),
    path("signup/", views.company_signup, name="company_signup"),
    path("login/", views.company_login, name="company_login"),
    #path("admin/review_queue/", views.review_queue, name="review_queue"),
    # path('admin/companies/review/', views.review_queue, name='review_queue'),
    path('review-queue/', views.review_queue, name='review_queue'),
    #path("dashboard/", views.company_dashboard, name="company_dashboard"),
    path('company-dashboard/', views.company_dashboard, name='company_dashboard'),  # Make sure the path is correct
    path("fetch-skills/", views.fetch_skills, name="fetch_skills"),  # New API endpoint
    #path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/project test 1.html',views.home,name='home'),
    
    path('features/upload3.html', views.recommend_resources, name='recommend_resources'),   # Add this line

]



#path('features/upload_resume5.html', views.upload_resume5, name='upload_resume5'),
    #path('recommend/', views.recommend_resources, name='recommend_resources'),
    #path('features/upload3.html', views.upload_resume6, name='upload_resume6'),
    #path('upload_resume6/', views.recommend_resources, name='recommend_resources'),
    
    
    
    #path('features/upload3.html', views.upload_resume6, name='upload_resume3'),
    
    #path('recommend-resources/', views.recommend_resources, name='recommend_resources'),  
    #path('upload_resume6/', views.recommend_resources, name='recommend_resources'),
    #path('features/upload3.html', views.upload_resume6, name='upload_resume3'),  # Upload form URL
    #path('recommend_resources/', views.recommend_resources, name='recommend_resources'),  # Recommend resources URL


    #path('upload/', views.recommend_courses, name='recommend_courses'),
    # path('upload/', views.upload_resume6, name='upload_resume6'),  # New upload page
    # path('process_resume/', views.recommend_courses, name='recommend_courses'),  # Processing route
    #path("resume-analysis/", views.resume_analysis, name="resume_analysis"),
    #path("upload-resume/", views.upload_resume, name="upload_resume"),





