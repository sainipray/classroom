# settings/urls.py
from django.urls import path

from .views import GetSettingsAPIView, UpdateSettingsAPIView

urlpatterns = [
    path("settings/", GetSettingsAPIView.as_view(), name="get-settings"),
    path("settings/update/", UpdateSettingsAPIView.as_view(), name="update-settings"),
]
