from django.urls import path
from .views import PushNotificationView

urlpatterns = [
    path('send-push-notification/', PushNotificationView.as_view(), name='send-push-notification'),
]
