import json
import logging
from datetime import datetime

import razorpay
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from apps.batch.models import BatchPurchaseOrder, LiveClass, Attendance
from config.razor_payment import RazorpayService

logger = logging.getLogger(__name__)
User = get_user_model()


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
            except ValueError as e:
                logger.error(f"Webhook payment verification failed: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            if verified_transaction.payment_status == 'completed':
                if verified_transaction.content_type == 'course':
                    # Existing course verification logic
                    pass  # Existing code
                elif verified_transaction.content_type == 'batch_installment':
                    # Handle batch installment verification
                    try:
                        purchase_order = BatchPurchaseOrder.objects.get(transaction=verified_transaction)
                    except BatchPurchaseOrder.DoesNotExist:
                        logger.error(f"No BatchPurchaseOrder found for transaction {razorpay_order_id}")
                        return Response({"error": "Invalid transaction."}, status=HTTP_400_BAD_REQUEST)

                    if not purchase_order.is_paid:
                        purchase_order.is_paid = True
                        purchase_order.payment_date = timezone.now()
                        purchase_order.save()
                        logger.info(
                            f"Installment {purchase_order.installment_number} for batch {purchase_order.batch.id} marked as paid via webhook.")
                else:
                    logger.error(
                        f"Invalid content type '{verified_transaction.content_type}' for transaction {razorpay_order_id}")
                    return Response({"error": "Invalid content type."}, status=HTTP_400_BAD_REQUEST)

                return Response({"message": "success"}, status=HTTP_200_OK)

        # Handle other event types if necessary
        return Response({"message": "ignored"}, status=HTTP_200_OK)


class MeritHubWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle the incoming POST requests from the webhook.
        """
        # Parse the incoming JSON payload
        data = request.data

        # Extract request type
        request_type = data.get("requestType", "unknown")  # Fallback to "unknown" if not provided

        # Log the received data to a file for inspection
        self.log_data_to_file(data, request_type)

        if request_type == "classStatus":
            return self.handle_class_status(data)
        elif request_type == "attendance":
            return self.handle_attendance(data)
        elif request_type == "recording":
            return self.handle_recording(data)
        elif request_type == "classFiles":
            return self.handle_class_files(data)
        elif request_type == "chats":
            return self.handle_chat_data(data)
        else:
            return Response({"message": "Unknown request type"}, status=HTTP_400_BAD_REQUEST)

    def log_data_to_file(self, data, request_type):
        """
        Log incoming data to a text file in the corresponding request type folder.
        """
        # Create the folder for the specific request type if it doesn't exist
        folder_path = settings.WEBHOOK_LOG_FOLDER / request_type
        folder_path.mkdir(parents=True, exist_ok=True)

        # Generate a unique filename using the current timestamp and UUID
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Full path for the log file
        file_path = folder_path / unique_filename

        # Write the data to the file
        with open(file_path, "w") as f:
            f.write(json.dumps(data, indent=4))

        print(f"Logged webhook data to {file_path}")

    def handle_class_status(self, data):
        """
        Handle class status updates.
        Status:
        Live: lv
        Ended: cp
        Cancelled: cl
        Expired: ex
        Edited: up
        """
        # Example: You can retrieve the data and save it to the database.
        class_id = data.get("classId")
        status = data.get("status")
        try:
            live_class = LiveClass.objects.get(class_id=class_id)
            live_class.status = status
            live_class.save()
            if status == 'lv':
                pass
                # TODO send notifications to all student for live class
        except LiveClass.DoesNotExist:
            print(f"Live class ID {class_id} not found")

        # Save the class status to the database or perform other actions
        # For now, just return a success response
        return Response({"message": "Class status processed"}, status=HTTP_200_OK)

    def handle_attendance(self, data):
        """
        Handle attendance data when the class has ended.
        """
        class_id = data.get("classId")
        attendance_data = data.get("attendance", [])
        try:
            live_class = LiveClass.objects.get(class_id=class_id)
            for attendance in attendance_data:
                merit_user_id = attendance.get("userId")
                try:
                    user = User.objects.get(merit_user_id=merit_user_id)
                    try:
                        attn = Attendance.objects.get(student=user, live_class=live_class)
                        attn.attended = True
                        attn.analytics = attendance.get('analytics')
                        attn.browser = attendance.get('browser')
                        attn.ip = attendance.get('ip')
                        attn.os = attendance.get('os')
                        attn.start_time = attendance.get('startTime')
                        attn.total_time = attendance.get('totalTime')
                        attn.save()
                    except Attendance.DoesNotExist:
                        print(f"Attendance not found the user {merit_user_id}")
                except User.DoesNotExist:
                    print("User does not exist")
        except LiveClass.DoesNotExist:
            print(f"Live class ID {class_id} not found")
        # Process and save attendance data to the database
        return Response({"message": "Attendance data processed"}, status=HTTP_200_OK)

    def handle_recording(self, data):
        """
        Handle recording status when available.
        """
        class_id = data.get("classId")
        recording_url = data.get("url")
        recording_status = data.get("status")
        duration = data.get("duration")
        try:
            live_class = LiveClass.objects.get(class_id=class_id)
            live_class.recording_url = recording_url
            live_class.recording_status = recording_status
            live_class.duration = duration
            live_class.save()
        except LiveClass.DoesNotExist:
            print(f"Live class ID {class_id} not found")
        # Process and save recording data to the database
        return Response({"message": "Recording processed"}, status=HTTP_200_OK)

    def handle_class_files(self, data):
        """
        Handle files shared during the class.
        """
        class_id = data.get("classId")
        files = data.get("Files", [])
        # Process and save the shared files data to the database
        return Response({"message": "Class files processed"}, status=HTTP_200_OK)

    def handle_chat_data(self, data):
        """
        Handle chat data when generated after class ends.
        """
        class_id = data.get("classId")
        chats = data.get("chats", {})
        # Process and save chat data (both public and private)
        return Response({"message": "Chat data processed"}, status=HTTP_200_OK)
