from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.course.student_views import AvailableCourseViewSet, PurchasedCourseCourseViewSet, \
    StudentCourseLiveClassesViewSet
from apps.course.views import CategoryViewSet, SubcategoryViewSet, CourseViewSet, FolderFileViewSet, \
    CreateCourseLiveClassView, CourseLiveClassViewSet, CourseReviewViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)
router.register(r'live-classes', CourseLiveClassViewSet, basename='course_live-classes')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'content', FolderFileViewSet, basename='course-content')
router.register('reviews', CourseReviewViewSet, basename='course-review')

# Student API router
student_router = DefaultRouter()
student_router.register(r'student/available-courses', AvailableCourseViewSet, basename='available-courses')
student_router.register(r'student/purchased-courses', PurchasedCourseCourseViewSet, basename='purchased-courses')

urlpatterns = [
    path('create-live-class/', CreateCourseLiveClassView.as_view(), name='create_live_class'),
    # Student URL
    path('student/<str:course>/course-live-classes/', StudentCourseLiveClassesViewSet.as_view({'get': 'list'}),
         name='live_classes_courses'),
    path('', include(router.urls)),
    path('', include(student_router.urls)),
]
