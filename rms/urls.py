"""
URL configuration for rms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from home import views



# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('home/',include('home.urls')),
#     path('',include('home.urls') ),

#     path('',views.home,name='home'),
#     path('login/', views.login_view, name='login'),

#     path('login.html', views.login_view, name='login'),
#     path('accounts/', include('django.contrib.auth.urls')),

#     path('', views.home_view, name='home'),
#     path('home/', views.home_view, name='home'),
#     path('signup.html', views.signup_view, name='signup'),

#     path('signup/', views.signup_view, name='signup'),

#     path('', views.home, name='home'),
#     path('afterlogin/', views.afterlogin_view, name='afterlogin'),
#     path('afterlogin.html', views.afterlogin_view, name='afterlogin'),
    
    
    
# ] 


# urlpatterns=[
#     path('', views.home, name='home'),
#    # path('login/', views.login_view, name='login'),
#     path('login.html', views.login_view, name='login'),
#     path('afterlogin/', views.afterlogin_view, name='afterlogin'),
#     path('features/', views.features, name='features'),

#     # Include Django's built-in authentication URLs
#     # path('accounts/', include('django.contrib.auth.urls')),
#     path('resume/', include('home.urls')),  # Include resume_review app URLs
    
#     path('features/upload.html', views.upload_resume, name='upload_resume'),  # Upload page
# ]



from django.urls import path
#from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login.html', views.login_view, name='login'),
    path('dashboard/login.html', views.login_view, name='login'),
    path('signup.html', views.signup_view, name='signup'),
    path('dashboard/signup.html', views.signup_view, name='signup'),
    path('afterlogin/', views.afterlogin_view, name='afterlogin'),
    path('features/', views.features, name='features'),
    path('features/upload.html', views.process_resume, name='upload_resume'),
    path('features/upload_resume.html', views.upload_resume2, name='upload_resume'),   # Add this line
    #path('process_resume/', views.process_resume, name='process_resume'),  # Add this line
    #path('features/upload3.html', views.recommend_resources, name='recommend_resources'),
    path('features/upload4.html', views.process_resume2, name='upload_resume3'),
    #path('features/view_resumes.html', views.view_resumes_inline, name='view_resumes'),
    path("signup/", views.company_signup, name="company_signup"),
    path("login/", views.company_login, name="company_login"),
    #path("admin/review-queue/", views.review_queue, name="review_queue"),
    # path('admin/companies/review/', views.review_queue, name='review_queue'),
    path('review-queue/', views.review_queue, name='review_queue'),
    #path("dashboard/", views.company_dashboard, name="company_dashboard"),
    path('company-dashboard/', views.company_dashboard, name='company_dashboard'),  # Make sure the path is correct
    path("fetch-skills/", views.fetch_skills, name="fetch_skills"),  # New API endpoint
    #path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/project test 1.html',views.home,name='home'),
    
    path('features/upload3.html', views.recommend_resources, name='recommend_resources'),   # Add this line

]


from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
]



#path('features/upload_resume5.html', views.upload_resume5, name='upload_resume5'),
    #path('recommend/', views.recommend_resources, name='recommend_resources'),
    #path('upload_resume6/', views.recommend_resources, name='upload_resume6'),
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



# # Serve media files during development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

