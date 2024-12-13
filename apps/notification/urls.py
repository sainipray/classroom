from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PushNotificationView, NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('send-push-notification/', PushNotificationView.as_view(), name='send-push-notification'),
    path('', include(router.urls)),
]
