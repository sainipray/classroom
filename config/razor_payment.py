# config/razor_payment.py

import razorpay
from django.conf import settings
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404
import logging

from apps.payment.models import Transaction
from apps.coupon.models import Coupon

logger = logging.getLogger(__name__)


class RazorpayService:
    def __init__(self):
        # Initialize Razorpay client with secure credentials from settings
        self.client = razorpay.Client(auth=('rzp_test_2cywPv1gKde6UC', 'ugceTueR2rPXQGjE2rcIwBfM'))

    def initiate_transaction(
            self,
            content_type,
            content_id,
            user,
            original_price,
            discount_applied,
            gst_percentage=0,
            coupon=None
    ):
        """
        Initiates a Razorpay transaction with optional coupon application.

        Parameters:
            - content_type (str): Type of content ('course', 'batch', 'test_series').
            - content_id (int): ID of the content being purchased.
            - user (User): The user making the purchase.
            - original_price (Decimal): Original price of the content.
            - discount_applied (Decimal): Discount applied to the original price.
            - gst_percentage (Decimal, optional): GST percentage to be applied. Defaults to 0.
            - coupon (Coupon, optional): Coupon applied to the transaction. Defaults to None.

        Returns:
            Transaction: The created Transaction object.
        """
        try:
            # Calculate price after discount
            price_after_coupon = original_price - discount_applied

            # Calculate GST amount
            gst_amount = (price_after_coupon * gst_percentage) / 100 if gst_percentage else 0

            # Calculate total amount to be charged
            total_amount = price_after_coupon + gst_amount

            # Create Razorpay order
            payment_order = self.client.order.create({
                "amount": int(total_amount * 100),  # Convert to paise
                "currency": "INR",
                "payment_capture": 1  # Auto capture
            })

            # Create Transaction record within an atomic transaction to ensure data integrity
            with db_transaction.atomic():
                transaction_record = Transaction.objects.create(
                    content_type=content_type,
                    content_id=content_id,
                    user=user,
                    amount=total_amount,
                    original_price=original_price,
                    discount_applied=discount_applied,
                    price_after_coupon=price_after_coupon,
                    gst_percentage=gst_percentage,
                    total_amount=total_amount,
                    coupon=coupon,
                    transaction_id=payment_order['id'],
                    payment_status='pending'
                )

            logger.info(f"Initiated transaction {transaction_record.transaction_id} for user {user.id}")
            return transaction_record

        except Exception as e:
            logger.error(f"Error initiating transaction: {str(e)}")
            raise

    def verify_payment(
            self,
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
    ):
        """
        Verifies the Razorpay payment signature and updates the Transaction status.

        Parameters:
            - razorpay_order_id (str): Razorpay Order ID.
            - razorpay_payment_id (str): Razorpay Payment ID.
            - razorpay_signature (str): Razorpay Signature.

        Returns:
            Transaction: The updated Transaction object.

        Raises:
            ValueError: If signature verification fails or transaction does not exist.
        """
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            # Verify the payment signature
            self.client.utility.verify_payment_signature(params_dict)
            logger.info(f"Signature verification successful for order {razorpay_order_id}")

            with db_transaction.atomic():
                # Retrieve the transaction and update its status
                transaction = Transaction.objects.select_for_update().get(transaction_id=razorpay_order_id)

                if transaction.payment_status == 'completed':
                    logger.info(f"Transaction {razorpay_order_id} already completed.")
                    return transaction  # Idempotent response

                transaction.payment_status = 'completed'
                transaction.payment_id = razorpay_payment_id
                transaction.save()

            logger.info(f"Transaction {razorpay_order_id} marked as completed.")
            return transaction

        except razorpay.errors.SignatureVerificationError:
            logger.warning(f"Signature verification failed for order {razorpay_order_id}")
            with db_transaction.atomic():
                try:
                    transaction = Transaction.objects.select_for_update().get(transaction_id=razorpay_order_id)
                    transaction.payment_status = 'failed'
                    transaction.save()
                    logger.info(f"Transaction {razorpay_order_id} marked as failed.")
                except Transaction.DoesNotExist:
                    logger.error(f"Transaction {razorpay_order_id} does not exist.")
                    raise ValueError('Transaction does not exist.')

            raise ValueError('Signature verification failed.')

        except Transaction.DoesNotExist:
            logger.error(f"Transaction {razorpay_order_id} does not exist.")
            raise ValueError('Transaction does not exist.')

        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            raise ValueError('Payment verification failed due to an internal error.')
