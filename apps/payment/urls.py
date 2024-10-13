from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.payment.views import PurchaseCourseView, VerifyPaymentView, TransactionViewSet, RazorpayWebhookView, \
    ApplyCouponView, GetCoursePricingView, PurchaseBatchView, GetBatchPricingView

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('purchase-course/', PurchaseCourseView.as_view(), name='purchase_course'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify_payment'),
    path('course-pricing/<int:course_id>/', GetCoursePricingView.as_view(), name='get_course_pricing'),
    path('apply-coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('webhook/', RazorpayWebhookView.as_view(), name='razorpay_webhook'),
    path('batch-pricing/<int:batch_id>/', GetBatchPricingView.as_view(), name='get_batch_pricing'),
    path('purchase-batch/', PurchaseBatchView.as_view(), name='purchase_batch'),
    path('', include(router.urls)),

]
