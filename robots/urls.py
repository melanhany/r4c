from django.urls import path
from . import views

urlpatterns = [
    path("api/robots/", views.post_robot),
    path("download_weekly_report/", views.generate_weekly_report),
]
