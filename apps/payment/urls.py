from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.payment.views import PurchaseCourseView, VerifyPaymentView, TransactionViewSet, \
    ApplyCouponView, GetCoursePricingView, PurchaseBatchView, GetBatchPricingView, PurchaseTestSeriesView, \
    GetTestSeriesPricingView

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('purchase-course/', PurchaseCourseView.as_view(), name='purchase_course'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify_payment'),
    path('course-pricing/<int:course_id>/', GetCoursePricingView.as_view(), name='get_course_pricing'),
    path('apply-coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('batch-pricing/<int:batch_id>/', GetBatchPricingView.as_view(), name='get_batch_pricing'),
    path('purchase-batch/', PurchaseBatchView.as_view(), name='purchase_batch'),
    path('test-series-pricing/<int:test_series_id>/', GetTestSeriesPricingView.as_view(),
         name='get_test_series_pricing'),
    path('purchase-test-series/', PurchaseTestSeriesView.as_view(), name='purchase_test_series'),

    path('', include(router.urls)),

]
