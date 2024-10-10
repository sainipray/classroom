from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .student_views import AvailableBatchViewSet, PurchasedBatchViewSet
from .views import SubjectViewSet, BatchViewSet, EnrollmentViewSet, LiveClassViewSet, AttendanceViewSet, \
    StudyMaterialViewSet, CreateLiveClassView, FeeStructureViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'batches', BatchViewSet)
router.register(r'live_classes', LiveClassViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'study-materials', StudyMaterialViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'fee-structures', FeeStructureViewSet)

student_router = DefaultRouter()
student_router.register(r'student/available-batches', AvailableBatchViewSet, basename='available-batches')
student_router.register(r'student/purchased-batches', PurchasedBatchViewSet, basename='purchased-batches')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(student_router.urls)),
    path('create-live-class/', CreateLiveClassView.as_view(), name='create_live_class'),

]
