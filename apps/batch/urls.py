from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, BatchViewSet, EnrollmentViewSet, LiveClassViewSet, AttendanceViewSet, StudyMaterialViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'batches', BatchViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'live_classes', LiveClassViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'study-materials', StudyMaterialViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
