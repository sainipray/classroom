from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.course.student_views import AvailableCourseViewSet, PurchasedCourseCourseViewSet
from apps.course.views import CategoryViewSet, SubcategoryViewSet, CourseViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)
router.register(r'courses', CourseViewSet, basename='course')

# Student API router
student_router = DefaultRouter()
student_router.register(r'student/available-courses', AvailableCourseViewSet, basename='available-courses')
student_router.register(r'student/purchased-courses', PurchasedCourseCourseViewSet, basename='purchased-courses')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(student_router.urls)),
]
