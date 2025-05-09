from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('resume/<int:pk>/', views.resume_detail, name='resume_detail'),
    path('resume/<int:pk>/save/', views.save_resume, name='save_resume'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('job-apply/', views.job_apply_url, name='apply_to_job'),
]
