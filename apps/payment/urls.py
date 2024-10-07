from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.payment.views import PurchaseCourseView, VerifyPaymentView, TransactionViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('purchase-course/', PurchaseCourseView.as_view(), name='purchase_course'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify_payment')
]
