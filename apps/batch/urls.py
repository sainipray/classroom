from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .student_views import AvailableBatchViewSet, PurchasedBatchViewSet, StudentLiveClassesViewSet, \
    StudentBatchAttendanceViewSet, StudentFeesRecordAPI
from .views import (SubjectViewSet, BatchViewSet, EnrollmentViewSet, LiveClassViewSet, AttendanceViewSet,
                    StudyMaterialViewSet, CreateLiveClassView, FeeStructureViewSet, FeesRecordAPI, FolderFileViewSet,
                    OfflineClassViewSet, StudentJoinBatchView)

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'batches', BatchViewSet)
router.register(r'live-classes', LiveClassViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'study-materials', StudyMaterialViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'fee-structures', FeeStructureViewSet)
router.register(r'content', FolderFileViewSet, basename='batch-content')
router.register(r'offline-classes', OfflineClassViewSet)

student_router = DefaultRouter()
student_router.register(r'student/available-batches', AvailableBatchViewSet, basename='available-batches')
student_router.register(r'student/purchased-batches', PurchasedBatchViewSet, basename='purchased-batches')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(student_router.urls)),
    path('create-live-class/', CreateLiveClassView.as_view(), name='create_live_class'),
    path('fees-record/', FeesRecordAPI.as_view(), name='fees_record'),
    path('student/join-batch/', StudentJoinBatchView.as_view(), name='join_batch'),

    # Student URL
    path('student/<str:batch>/batches-live-classes/', StudentLiveClassesViewSet.as_view({'get': 'list'}),
         name='live_classes_batches'),
    path('student/<str:batch>/batches-attendance/', StudentBatchAttendanceViewSet.as_view({'get': 'list'}),
         name='student_batch_attendance'),
    path('student-fees-record/', StudentFeesRecordAPI.as_view(), name='student_fees_record'),

]
