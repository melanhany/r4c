from django.urls import path
from . import views

urlpatterns = [path("api/customers/", views.post_customer)]
