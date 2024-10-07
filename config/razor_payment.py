import razorpay
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from apps.payment.models import Transaction

User = get_user_model()

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=('rzp_test_2cywPv1gKde6UC', 'ugceTueR2rPXQGjE2rcIwBfM'))

    def initiate_transaction(self, content_type, content_id, user, amount):
        """
        Initiates a Razorpay transaction.
        """
        # Create Razorpay order
        payment_order = self.client.order.create({
            "amount": int(amount * 100),  # Convert to paise
            "currency": "INR",
            "payment_capture": 1  # Auto capture
        })

        # Create Transaction record
        transaction = Transaction.objects.create(
            content_type=content_type,
            content_id=content_id,
            user=user,
            amount=amount,
            transaction_id=payment_order['id'],
            payment_status='pending'
        )
        return transaction

    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verifies the Razorpay payment signature.
        """
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            self.client.utility.verify_payment_signature(params_dict)
            # Update transaction status to completed
            transaction = get_object_or_404(Transaction, transaction_id=razorpay_order_id)
            transaction.payment_status = 'completed'
            transaction.save()
            return transaction
        except razorpay.errors.SignatureVerificationError:
            # Update transaction status to failed
            transaction = get_object_or_404(Transaction, transaction_id=razorpay_order_id)
            transaction.payment_status = 'failed'
            transaction.save()
            raise ValueError('Signature verification failed.')
