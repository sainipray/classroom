from rest_framework.views import APIView
from rest_framework.response import Response
from push_notifications.models import GCMDevice
from .serializers import PushNotificationSerializer
from apps.course.models import CoursePurchaseOrder
from .models import PushNotification  # Import the model

class PushNotificationView(APIView):

    def post(self, request):
        serializer = PushNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        title = validated_data["title"]
        message = validated_data["message"]
        criteria = validated_data["criteria"]

        devices = GCMDevice.objects.none()

        # Fetch devices based on criteria
        if criteria == "course":
            course = validated_data["course"]  # Instance of Course
            paid_students = CoursePurchaseOrder.objects.filter(
                course=course, is_paid=True
            ).values_list("student__id", flat=True)
            devices = GCMDevice.objects.filter(user__id__in=paid_students)
        elif criteria == "batch":
            batch = validated_data["batch"]  # Instance of Batch
            approved_students = batch.enrollments.filter(
                is_approved=True
            ).values_list("student__id", flat=True)
            devices = GCMDevice.objects.filter(user__id__in=approved_students)
        elif criteria == "manual":
            student_ids = validated_data["student_ids"]
            devices = GCMDevice.objects.filter(user__id__in=student_ids)
        elif criteria == "general":
            devices = GCMDevice.objects.filter(active=True)

        # # Send push notifications
        # devices.send_message({"title": title, "body": message})

        # Save the push notification in the database
        notification = PushNotification.objects.create(
            title=title,
            message=message,
            criteria=criteria,
            course=validated_data.get("course", None),
            batch=validated_data.get("batch", None),
            student_ids=validated_data.get("student_ids", []),  # Save student IDs as an array
        )

        return Response({"message": "Notification sent and saved successfully."})
