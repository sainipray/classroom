import logging
import tempfile
from decimal import Decimal

from django.conf import settings
from django.db import transaction as db_transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from weasyprint import HTML

from abstract.views import ReadOnlyCustomResponseMixin
from apps.batch.models import BatchPurchaseOrder, Batch, Enrollment
from apps.course.models import Course, CoursePurchaseOrder, CourseValidityPeriod
from apps.payment.models import Transaction
from apps.payment.serializers import VerifyPaymentSerializer, TransactionSerializer, PurchaseCourseSerializer, \
    ApplyCouponSerializer, PurchaseBatchSerializer, PurchaseTestSeriesSerializer
from apps.test_series.models import TestSeries, TestSeriesPurchaseOrder
from config.razor_payment import RazorpayService

logger = logging.getLogger(__name__)


def final_price_with_other_expenses_and_gst(original_price, discounted_price=None):
    # Define other fees (these could be defined in settings or calculated)
    internet_charges = getattr(settings, 'INTERNET_CHARGES', Decimal('10.00'))  # Example fixed internet charges
    platform_fees = getattr(settings, 'PLATFORM_FEE', Decimal('10.00'))  # Example fixed platform fee
    # Calculate GST
    gst_percentage = getattr(settings, 'GST_PERCENTAGE', Decimal('18.0'))  # Define GST_PERCENTAGE in settings.py
    if discounted_price:
        gst_amount = (Decimal(discounted_price) + internet_charges + platform_fees) * Decimal(gst_percentage) / Decimal(
            '100')
        total_amount = Decimal(discounted_price) + gst_amount + internet_charges + platform_fees
    else:
        gst_amount = (Decimal(original_price) + internet_charges + platform_fees) * Decimal(gst_percentage) / Decimal(
            '100')
        total_amount = Decimal(original_price) + gst_amount + internet_charges + platform_fees
    data = {
        "original_price": Decimal(original_price),
        "gst_percentage": gst_percentage,
        "gst_amount": gst_amount.quantize(Decimal('0.01')),
        "internet_charges": internet_charges,
        "platform_fees": platform_fees,
        "total_amount": total_amount.quantize(Decimal('0.01'))
    }
    return data


class TransactionViewSet(ReadOnlyCustomResponseMixin):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, pk=None):
        transaction = self.get_object()
        # Render the HTML template with context data
        html_string = render_to_string('invoice/invoice.html', {'transaction': transaction})

        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
            HTML(string=html_string).write_pdf(temp_pdf.name)

            # Read the PDF and return it as an HTTP response
            with open(temp_pdf.name, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="transaction_{transaction.id}.pdf"'
                return response


class GetCoursePricingView(APIView):
    """
    API view to get pricing details for a specific course including GST and additional fees.
    """

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, is_published=True)
        # Original price
        original_price = course.effective_price or 0
        validity_period = request.query_params.get('validity_period')
        if validity_period:
            validity_period = int(validity_period)
            original_price = CourseValidityPeriod.objects.get(course=course, id=validity_period).effective_price

        final_price_responses = final_price_with_other_expenses_and_gst(original_price)

        # Construct the response data
        response_data = {
            "course_id": course.id,
            "course_name": course.name,
        }
        response_data.update(final_price_responses)

        return Response(response_data, status=status.HTTP_200_OK)


class GetBatchPricingView(APIView):
    """
    API view to get pricing details for a specific batch including GST and additional fees.
    """

    def get(self, request, batch_id, installment_number):
        batch = get_object_or_404(Batch, id=batch_id, is_published=True)  # Ensure to check if the batch is active
        # Original price (assuming first installment is stored in a field called `first_installment_price`)
        original_price = batch.fee_structure.fee_amount or 0

        # Get final pricing details including GST and other fees
        final_price_responses = final_price_with_other_expenses_and_gst(original_price)

        # Construct the response data
        response_data = {
            "batch_id": batch.id,
            "batch_name": batch.name,
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
        validity_period = serializer.validated_data.get('validity_period')
        course = get_object_or_404(Course, id=course_id, is_published=True)

        # Check if the user has already purchased the course
        if CoursePurchaseOrder.objects.filter(student=request.user, course=course).exists():
            logger.info(f"User {request.user.id} attempted to repurchase course {course_id}.")
            return Response({"error": "You have already purchased this course."}, status=status.HTTP_400_BAD_REQUEST)

        original_price = course.effective_price or 0
        discount_applied = 0
        price_after_coupon = None
        if validity_period:
            validity_period = int(validity_period)
            original_price = CourseValidityPeriod.objects.get(course=course, id=validity_period).effective_price

        if coupon:
            # Apply discount using the enhanced apply_discount method
            price_after_coupon, discount_applied = coupon.apply_discount(original_price, request.user, course)

            final_price_responses = final_price_with_other_expenses_and_gst(Decimal(original_price),
                                                                            Decimal(price_after_coupon))
        else:
            final_price_responses = final_price_with_other_expenses_and_gst(Decimal(original_price))
        try:
            razorpay_service = RazorpayService()
            transaction = razorpay_service.initiate_transaction(
                content_type=Transaction.ContentType.COURSE,
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
        try:
            CoursePurchaseOrder.objects.create(
                student=request.user,
                course=course,
                transaction=transaction,
                amount=final_price_responses['total_amount'],
                course_validity_id=validity_period,

            )
            logger.info(
                f"CoursePurchaseOrder created for transaction {transaction.transaction_id} by user {request.user.id}"
            )
        except Exception as e:
            logger.error(f"Failed to create CoursePurchaseOrder: {str(e)}")
            return Response({"error": "Failed to create purchase order."},
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


class GetTestSeriesPricingView(APIView):
    """
    API view to get pricing details for a specific test series including GST and additional fees.
    """

    def get(self, request, test_series_id):
        test_series = get_object_or_404(TestSeries, id=test_series_id,
                                        is_published=True)  # Ensure to check if the test series is active

        # Original price (assuming first installment is stored in a field called `first_installment_price`)
        original_price = test_series.effective_price or 0

        # Get final pricing details including GST and other fees
        final_price_responses = final_price_with_other_expenses_and_gst(original_price)

        # Construct the response data
        response_data = {
            "test_series_id": test_series.id,
            "test_series_name": test_series.name,
        }
        response_data.update(final_price_responses)

        return Response(response_data, status=status.HTTP_200_OK)


class PurchaseTestSeriesView(APIView):
    """
    API view to initiate a test series purchase by creating a Razorpay order.
    """

    def post(self, request):
        serializer = PurchaseTestSeriesSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        test_series = serializer.validated_data['test_series']

        # Check if the user has already purchased the test series
        if TestSeriesPurchaseOrder.objects.filter(student=request.user, test_series=test_series).exists():
            return Response({"error": "You have already purchased this test series."},
                            status=status.HTTP_400_BAD_REQUEST)

        original_price = test_series.effective_price or 0
        discount_applied = 0
        price_after_coupon = None

        final_price_responses = final_price_with_other_expenses_and_gst(Decimal(original_price))

        try:
            razorpay_service = RazorpayService()
            transaction = razorpay_service.initiate_transaction(
                content_type=Transaction.ContentType.TEST_SERIES,
                content_id=test_series.id,
                user=request.user,
                discount_applied=discount_applied,
                coupon=None,
                price_after_coupon=price_after_coupon,
                total_amount=final_price_responses['total_amount'],
                original_price=final_price_responses['original_price'],
                gst_percentage=final_price_responses['gst_percentage'],
                platform_fees=final_price_responses['platform_fees'],
                internet_charges=final_price_responses['internet_charges'],
            )
        except Exception as e:
            return Response({"error": "Failed to initiate transaction. Please try again later."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            "order_id": transaction.transaction_id,
            "amount": float(transaction.amount),
            "currency": "INR",
            "name": getattr(settings, 'WEB_SITE_NAME', 'Your Website Name'),  # Define in settings.py
            "description": f"Payment for Test Series: {test_series.name}",
            "image": "",  # Define in settings.py
            "prefill": {
                "name": request.user.full_name,
                "email": request.user.email,
                "contact": request.user.phone_number.as_e164  # Ensure `phone_number` is properly handled
            }
        }

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

            # Handle different content types
            content_type = verified_transaction.content_type
            content_id = verified_transaction.content_id

            if content_type == Transaction.ContentType.COURSE:
                try:
                    purchase_order = CoursePurchaseOrder.objects.get(transaction=verified_transaction)
                except BatchPurchaseOrder.DoesNotExist:
                    logger.error(f"No CoursePurchaseOrder found for transaction {razorpay_order_id}")
                    return Response({"error": "Invalid transaction."}, status=status.HTTP_400_BAD_REQUEST)

                if purchase_order.is_paid:
                    logger.info(
                        f"Already paid for transaction {razorpay_order_id}.")
                    return Response({"status": "Payment already verified and marked as paid."},
                                    status=status.HTTP_200_OK)

                purchase_order.is_paid = True
                purchase_order.payment_date = timezone.now()
                purchase_order.course_joined_date = timezone.now()
                purchase_order.save()

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
            elif content_type == Transaction.ContentType.BATCH:
                # Handle batch installment verification
                try:
                    purchase_order = BatchPurchaseOrder.objects.get(transaction=verified_transaction)
                except BatchPurchaseOrder.DoesNotExist:
                    logger.error(f"No BatchPurchaseOrder found for transaction {razorpay_order_id}")
                    return Response({"error": "Invalid transaction."}, status=status.HTTP_400_BAD_REQUEST)

                if purchase_order.is_paid:
                    logger.info(
                        f"Installment {purchase_order.installment_number} already paid for transaction {razorpay_order_id}.")
                    return Response({"status": "Payment already verified and installment marked as paid."},
                                    status=status.HTTP_200_OK)

                # Mark the installment as paid
                purchase_order.is_paid = True
                purchase_order.payment_date = timezone.now()
                purchase_order.save()

                logger.info(
                    f"Installment {purchase_order.installment_number} for batch {purchase_order.batch.id} marked as paid.")

                # Enroll the student in the batch
                if not Enrollment.objects.filter(batch=purchase_order.batch, student=request.user).exists():
                    Enrollment.objects.create(
                        batch=purchase_order.batch,
                        student=request.user,
                        is_approved=True  # Set approval status as needed
                    )
                    logger.info(f"Student {request.user.id} enrolled in batch {purchase_order.batch.id}.")

                return Response({"status": "Payment verified and installment marked as paid."},
                                status=status.HTTP_200_OK)

            elif content_type == Transaction.ContentType.TEST_SERIES:
                test_series = get_object_or_404(TestSeries, id=content_id, is_published=True)

                # Create TestSeriesPurchaseOrder
                TestSeriesPurchaseOrder.objects.create(
                    student=request.user,
                    test_series=test_series,
                    transaction=verified_transaction
                )
                logger.info(
                    f"TestSeriesPurchaseOrder created for transaction {razorpay_order_id} and user {request.user.id}")

                return Response({"status": "Payment verified and test series purchase order created."},
                                status=status.HTTP_200_OK)

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
        serializer.is_valid(raise_exception=True)
        course_id = serializer.validated_data['course_id']
        coupon = serializer.validated_data['coupon_code']
        course = get_object_or_404(Course, id=course_id)
        original_price = course.effective_price

        price_after_coupon, discount_amount = coupon.apply_discount(original_price, request.user, course)
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


class PurchaseBatchView(APIView):
    """
    API view to initiate a batch purchase by creating a Razorpay order for a specific installment.
    If installment_number is not provided, it initiates payment for the first unpaid installment by default.
    """

    @db_transaction.atomic
    def post(self, request):
        serializer = PurchaseBatchSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        batch = serializer.validated_data['batch']
        fee_structure = serializer.validated_data['fee_structure']
        installment_number = serializer.validated_data.get('installment_number')

        # If installment_number is not provided, find the first unpaid installment
        if not installment_number:
            try:
                first_unpaid_order = BatchPurchaseOrder.objects.filter(
                    student=request.user,
                    batch=batch,
                    is_paid=False
                ).order_by('installment_number').first()
                if first_unpaid_order:
                    installment_number = first_unpaid_order.installment_number
                else:
                    # If no existing purchase orders, start with installment 1
                    installment_number = 1
            except BatchPurchaseOrder.DoesNotExist:
                installment_number = 1

        fee_amount = fee_structure.fee_amount
        original_price = fee_amount

        # Calculate final price with fees and GST
        final_price_responses = final_price_with_other_expenses_and_gst(Decimal(original_price))

        try:
            razorpay_service = RazorpayService()
            transaction = razorpay_service.initiate_transaction(
                content_type=Transaction.ContentType.BATCH,
                content_id=batch.id,
                user=request.user,
                discount_applied=0,  # Adjust if discounts are applied
                coupon=None,  # Adjust if coupons are used
                price_after_coupon=final_price_responses['total_amount'],
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

        try:
            BatchPurchaseOrder.objects.create(
                student=request.user,
                batch=batch,
                transaction=transaction,
                installment_number=installment_number,
                amount=final_price_responses['total_amount']
            )
            logger.info(
                f"BatchPurchaseOrder created for transaction {transaction.transaction_id} by user {request.user.id}"
            )
        except Exception as e:
            logger.error(f"Failed to create BatchPurchaseOrder: {str(e)}")
            return Response({"error": "Failed to create purchase order."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            "order_id": transaction.transaction_id,
            "amount": float(transaction.amount),
            "currency": "INR",
            "name": getattr(settings, 'WEB_SITE_NAME', 'Your Site Name'),
            "description": f"Payment for Batch: {batch.name} - Installment {installment_number}",
            "image": getattr(settings, 'WEB_SITE_IMAGE', ""),
            "prefill": {
                "name": request.user.full_name,
                "email": request.user.email,
                "contact": request.user.phone_number.as_e164
            }
        }

        logger.info(
            f"Transaction {transaction.transaction_id} initiated for batch {batch.id}, installment {installment_number} by user {request.user.id}"
        )
        return Response(response_data, status=status.HTTP_200_OK)
