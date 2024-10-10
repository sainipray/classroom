import logging

from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from abstract.views import ReadOnlyCustomResponseMixin
from apps.course.models import Course, CoursePurchaseOrder
from apps.payment.models import Transaction
from apps.payment.serializers import VerifyPaymentSerializer, TransactionSerializer, PurchaseCourseSerializer
from config.razor_payment import RazorpayService

logger = logging.getLogger(__name__)


class TransactionViewSet(ReadOnlyCustomResponseMixin):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class PurchaseCourseView(APIView):
    """
    API view to initiate a course purchase by creating a Razorpay order.
    """

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

        original_price = course.price or 0
        discount_applied = 0

        if coupon:
            discount_applied = coupon.apply_discount(original_price)
            discount_applied = original_price - discount_applied  # Calculate the discount amount

        # TODO
        gst_percentage = 18  # settings.GST_PERCENTAGE  # Define GST_PERCENTAGE in settings.py

        try:
            razorpay_service = RazorpayService()
            transaction = razorpay_service.initiate_transaction(
                content_type='course',
                content_id=course.id,
                user=request.user,
                original_price=original_price,
                discount_applied=discount_applied,
                gst_percentage=gst_percentage,
                coupon=coupon
            )
        except Exception as e:
            logger.error(f"Failed to initiate transaction for user {request.user.id}: {str(e)}")
            return Response({"error": "Failed to initiate transaction. Please try again later."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            "order_id": transaction.transaction_id,
            "amount": float(transaction.amount),
            "currency": "INR",
            # TODO
            "name": "Baluja Classes",  # settings.WEBSITE_NAME,  # Define WEBSITE_NAME in settings.py
            "description": f"Payment for Course: {course.name}",
            # TODO
            "image": "demo",  # settings.WEBSITE_LOGO_URL,  # Define WEBSITE_LOGO_URL in settings.py
            "prefill": {
                "name": request.user.full_name,
                "email": request.user.email,
                "contact": request.user.phone_number.as_e164
            }
        }

        logger.info(f"Transaction {transaction.transaction_id} initiated for user {request.user.id}")
        return Response(response_data, status=status.HTTP_200_OK)


class VerifyPaymentView(APIView):
    """
    API view to verify Razorpay payments and create purchase orders upon successful payment.
    """

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
                    logger.info(f"CoursePurchaseOrder created for transaction {razorpay_order_id} and user {request.user.id}")
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
                        logger.error(f"Failed to increment coupon usage for {verified_transaction.coupon.code}: {str(e)}")
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

            return Response({"status": "Payment verified and purchase order created successfully."}, status=status.HTTP_200_OK)

        else:
            logger.warning(f"Payment verification failed for transaction {razorpay_order_id}. Status: {verified_transaction.payment_status}")
            return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)
