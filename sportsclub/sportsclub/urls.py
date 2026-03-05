# sportsclub/urls.py
"""URL configuration for sportsclub project."""

from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from sportsclub.api import api

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
