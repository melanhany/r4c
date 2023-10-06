from django.urls import path
from . import views

urlpatterns = [
    path("api/robots/", views.post_robot)
]
