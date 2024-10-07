from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from abstract.views import ReadOnlyCustomResponseMixin
from apps.course.models import Course, CoursePurchaseOrder
from apps.payment.models import Transaction
from apps.payment.serializers import VerifyPaymentSerializer, TransactionSerializer
from config.razor_payment import RazorpayService


class TransactionViewSet(ReadOnlyCustomResponseMixin):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class PurchaseCourseView(APIView):
    def post(self, request):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        amount = course.effective_price

        # Initiate Razorpay transaction
        razorpay_service = RazorpayService()
        transaction = razorpay_service.initiate_transaction('course', content_id=course_id, user=request.user,
                                                            amount=amount)

        return Response({
            "order_id": transaction.transaction_id,
            "amount": float(transaction.amount),
            "currency": "INR",
            "name": "Your Website Name",
            "description": f"Payment for Course ID {course_id}",
            "image": "https://yourwebsite.com/static/images/logo.png",  # Optional
            "prefill": {
                "name": request.user.full_name,
                "email": request.user.email,
                "contact": request.user.phone_number.as_e164
            }
        }, status=status.HTTP_200_OK)


class VerifyPaymentView(APIView):

    def post(self, request):
        """
        Verifies a payment by checking the Razorpay signature.
        Expects 'razorpay_order_id', 'razorpay_payment_id', and 'razorpay_signature' in the request data.
        """
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        razorpay_order_id = serializer.validated_data['razorpay_order_id']
        razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
        razorpay_signature = serializer.validated_data['razorpay_signature']

        # Verify payment
        razorpay_service = RazorpayService()
        transaction = razorpay_service.verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature)
        if transaction and transaction.payment_status == 'completed':
            content_type = transaction.content_type
            if content_type == 'course':
                # Get the course and user from the transaction data
                course_id = transaction.content_id  # Adjust according to your transaction structure
                course = get_object_or_404(Course, id=course_id)

                # # Create a CoursePurchaseOrder entry
                # order = CoursePurchaseOrder.objects.create(
                #     user=request.user,
                #     course=course,
                #     original_price=course.price,
                #     effective_price=transaction.amount,  # Assuming amount matches the effective price
                #     # Set additional fields as necessary
                # )
            # todo handle batch and test series
            return Response({"status": "Payment verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)
