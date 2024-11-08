# settings/urls.py
from django.urls import path

from .views import GetSettingsAPIView, UpdateSettingsAPIView

urlpatterns = [
    path("retrieve/", GetSettingsAPIView.as_view(), name="get-settings"),
    path("update/", UpdateSettingsAPIView.as_view(), name="update-settings"),
]
