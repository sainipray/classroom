import logging
from decimal import Decimal

import razorpay
from django.conf import settings
from django.db import transaction as db_transaction
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from abstract.views import ReadOnlyCustomResponseMixin
from apps.course.models import Course, CoursePurchaseOrder
from apps.payment.models import Transaction
from apps.payment.serializers import VerifyPaymentSerializer, TransactionSerializer, PurchaseCourseSerializer, \
    ApplyCouponSerializer
from config.razor_payment import RazorpayService

logger = logging.getLogger(__name__)


def final_price_with_other_expenses_and_gst(original_price, discounted_price=None):
    # Define other fees (these could be defined in settings or calculated)
    internet_charges = getattr(settings, 'INTERNET_CHARGES', 10)  # Example fixed internet charges
    platform_fees = getattr(settings, 'PLATFORM_FEE', 10)  # Example fixed platform fee
    # Calculate GST
    gst_percentage = getattr(settings, 'GST_PERCENTAGE', 18.0)  # Define GST_PERCENTAGE in settings.py
    if discounted_price:
        gst_amount = Decimal(discounted_price + internet_charges + platform_fees) * Decimal(gst_percentage) / 100
        total_amount = discounted_price + gst_amount + internet_charges + platform_fees
    else:
        gst_amount = Decimal(original_price + internet_charges + platform_fees) * Decimal(gst_percentage) / 100
        total_amount = original_price + gst_amount + internet_charges + platform_fees
    data = {
        "original_price": original_price,
        "gst_percentage": gst_percentage,
        "gst_amount": gst_amount,
        "internet_charges": internet_charges,
        "platform_fees": platform_fees,
        "total_amount": total_amount
    }
    return data


class TransactionViewSet(ReadOnlyCustomResponseMixin):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class GetCoursePricingView(APIView):
    """
    API view to get pricing details for a specific course including GST and additional fees.
    """

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, is_published=True)

        # Original price
        original_price = course.effective_price or 0

        final_price_responses = final_price_with_other_expenses_and_gst(original_price)

        # Construct the response data
        response_data = {
            "course_id": course.id,
            "course_name": course.name,
        }
        response_data.update(final_price_responses)

        return Response(response_data, status=status.HTTP_200_OK)


class PurchaseCourseView(APIView):
    """
    API view to initiate a course purchase by creating a Razorpay order.
    """

    @db_transaction.atomic
    def post(self, request):
        serializer = PurchaseCourseSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']
        coupon = serializer.validated_data.get('coupon_code')  # This is a Coupon instance or None

        course = get_object_or_404(Course, id=course_id, is_published=True)

        # Check if the user has already purchased the course
        if CoursePurchaseOrder.objects.filter(student=request.user, course=course).exists():
            logger.info(f"User {request.user.id} attempted to repurchase course {course_id}.")
            return Response({"error": "You have already purchased this course."}, status=status.HTTP_400_BAD_REQUEST)

        original_price = course.effective_price or 0
        discount_applied = 0
        price_after_coupon = None
        if coupon:
            # Apply discount using the enhanced apply_discount method
            price_after_coupon, discount_applied = coupon.apply_discount(original_price)

        final_price_responses = final_price_with_other_expenses_and_gst(Decimal(original_price),
                                                                        Decimal(price_after_coupon))

        try:
            razorpay_service = RazorpayService()
            transaction = razorpay_service.initiate_transaction(
                content_type='course',
                content_id=course.id,
                user=request.user,
                discount_applied=discount_applied,
                coupon=coupon,
                price_after_coupon=price_after_coupon,
                total_amount=final_price_responses['total_amount'],
                original_price=final_price_responses['original_price'],
                gst_percentage=final_price_responses['gst_percentage'],
                platform_fees=final_price_responses['platform_fees'],
                internet_charges=final_price_responses['internet_charges'],
            )
        except Exception as e:
            logger.error(f"Failed to initiate transaction for user {request.user.id}: {str(e)}")
            return Response({"error": "Failed to initiate transaction. Please try again later."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            "order_id": transaction.transaction_id,
            "amount": float(transaction.amount),
            "currency": "INR",
            "name": getattr(settings, 'WEB_SITE_NAME', 'Baluja Classes'),  # Define in settings.py
            "description": f"Payment for Course: {course.name}",
            "image": "",  # Define in settings.py
            "prefill": {
                "name": request.user.full_name,
                "email": request.user.email,
                "contact": request.user.phone_number.as_e164  # Ensure `phone_number` is properly handled
            }
        }

        logger.info(f"Transaction {transaction.transaction_id} initiated for user {request.user.id}")
        return Response(response_data, status=status.HTTP_200_OK)


class VerifyPaymentView(APIView):
    """
    API view to verify Razorpay payments and create purchase orders upon successful payment.
    """

    @db_transaction.atomic
    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        razorpay_order_id = serializer.validated_data['razorpay_order_id']
        razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
        razorpay_signature = serializer.validated_data['razorpay_signature']

        # Retrieve the transaction and ensure it belongs to the authenticated user
        transaction = get_object_or_404(Transaction, transaction_id=razorpay_order_id, user=request.user)

        # Verify payment
        razorpay_service = RazorpayService()
        try:
            verified_transaction = razorpay_service.verify_payment(
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature
            )
        except ValueError as e:
            logger.warning(f"Payment verification failed for transaction {razorpay_order_id}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if verified_transaction.payment_status == 'completed':
            # Check if the purchase order already exists to ensure idempotency
            if CoursePurchaseOrder.objects.filter(transaction=verified_transaction).exists():
                logger.info(f"Purchase order already created for transaction {razorpay_order_id}.")
                return Response({"status": "Payment already verified and order created."}, status=status.HTTP_200_OK)

            # Handle different content types
            content_type = verified_transaction.content_type
            content_id = verified_transaction.content_id

            if content_type == 'course':
                course = get_object_or_404(Course, id=content_id)
                try:
                    # Create CoursePurchaseOrder
                    CoursePurchaseOrder.objects.create(
                        student=request.user,
                        course=course,
                        transaction=verified_transaction
                    )
                    logger.info(
                        f"CoursePurchaseOrder created for transaction {razorpay_order_id} and user {request.user.id}")
                except Exception as e:
                    logger.error(f"Failed to create CoursePurchaseOrder for transaction {razorpay_order_id}: {str(e)}")
                    return Response({"error": "Payment verified, but failed to create purchase order."},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Increment coupon usage if a coupon was used
                if verified_transaction.coupon:
                    try:
                        verified_transaction.coupon.increment_usage()
                        logger.info(f"Coupon {verified_transaction.coupon.code} usage incremented.")
                    except Exception as e:
                        logger.error(
                            f"Failed to increment coupon usage for {verified_transaction.coupon.code}: {str(e)}")
                        # Optionally, handle this scenario (e.g., notify admin)

            # TODO: Handle other content types like 'batch' and 'test_series'
            elif content_type == 'batch':
                # Implement batch purchase logic
                pass
            elif content_type == 'test_series':
                # Implement test series purchase logic
                pass
            else:
                logger.error(f"Invalid content type '{content_type}' for transaction {razorpay_order_id}")
                return Response({"error": "Invalid content type."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"status": "Payment verified and purchase order created successfully."},
                            status=status.HTTP_200_OK)

        else:
            logger.warning(
                f"Payment verification failed for transaction {razorpay_order_id}. Status: {verified_transaction.payment_status}")
            return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)


class ApplyCouponView(APIView):
    """
    API view to apply a coupon code to a course and retrieve discount details.
    """

    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            coupon = serializer.validated_data['coupon_code']
            course = get_object_or_404(Course, id=course_id)
            original_price = course.effective_price or 0

            # Apply discount
            price_after_coupon, discount_amount = coupon.apply_discount(original_price)
            final_price_responses = final_price_with_other_expenses_and_gst(Decimal(original_price),
                                                                            Decimal(price_after_coupon))

            # Prepare response data
            response_data = {
                "discounted_price": float(price_after_coupon),
                "discount_amount": float(discount_amount),
                "coupon": {
                    "id": coupon.id,
                    "code": coupon.code,
                    "name": coupon.name,
                    "discount_type": coupon.discount_type,
                    "discount_value": float(coupon.discount_value),
                    "max_discount_amount": float(coupon.max_discount_amount) if coupon.max_discount_amount else None
                }
            }
            response_data.update(final_price_responses)

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RazorpayWebhookView(APIView):
    """
    Endpoint to handle Razorpay webhook events.
    """
    permission_classes = [AllowAny]  # Razorpay needs to access this endpoint

    def post(self, request):
        payload = request.body
        signature = request.headers.get('X-Razorpay-Signature')

        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET  # Define in settings.py

        try:
            # Verify webhook signature
            razorpay_client = RazorpayService()
            razorpay_client.utility.verify_webhook_signature(payload, signature, webhook_secret)
            event = razorpay_client.utility.parse_webhook_event(payload)
        except razorpay.errors.SignatureVerificationError:
            logger.warning("Invalid Razorpay webhook signature.")
            return Response({"error": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error parsing Razorpay webhook: {str(e)}")
            return Response({"error": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)

        event_type = event.get('event')
        data = event.get('payload', {}).get('payment', {}).get('entity', {})

        if event_type == 'payment.captured':
            razorpay_order_id = data.get('order_id')
            razorpay_payment_id = data.get('id')
            # Assuming signature verification has already been done

            try:
                razorpay_service = RazorpayService()
                verified_transaction = razorpay_service.verify_payment(
                    razorpay_order_id=razorpay_order_id,
                    razorpay_payment_id=razorpay_payment_id,
                    razorpay_signature=signature  # Adjust as needed
                )
                return Response({"status": "success"}, status=status.HTTP_200_OK)
            except ValueError as e:
                logger.error(f"Webhook payment verification failed: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Handle other event types if necessary
        return Response({"status": "ignored"}, status=status.HTTP_200_OK)
