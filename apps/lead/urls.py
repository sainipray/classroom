from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet

router = DefaultRouter()
router.register(r'leads', LeadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
