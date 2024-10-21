from django.urls import path

from apps.webhook.views import RazorpayWebhookView, MeritHubWebhookView

urlpatterns = [
    path('razorpay/', RazorpayWebhookView.as_view(), name='razorpay_webhook'),
    path('merithub/', MeritHubWebhookView.as_view(), name='merit_hub_webhook'),

]
