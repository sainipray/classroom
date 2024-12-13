from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.batch.models import Batch
from apps.course.models import Course
from apps.notification.models import PushNotification

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    batch_title = serializers.SerializerMethodField()
    student_names = serializers.SerializerMethodField()

    class Meta:
        model = PushNotification
        fields = '__all__'  # Include all fields from the model
        extra_fields = ['course_title', 'batch_title', 'student_names']

    def get_course_title(self, obj):
        if obj.course:
            return obj.course.name  # Assuming Course model has a `title` field
        return None

    def get_batch_title(self, obj):
        if obj.batch:
            return obj.batch.name  # Assuming Batch model has a `title` field
        return None

    def get_student_names(self, obj):
        if obj.student_ids:
            students = User.objects.filter(id__in=obj.student_ids).values_list("full_name", flat=True)
            return list(students)
        return []



class PushNotificationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=True)
    message = serializers.CharField(required=True)
    criteria = serializers.ChoiceField(choices=["course", "batch", "student", "general"], required=True)
    course = serializers.IntegerField(required=False)  # Frontend sends this
    batch = serializers.IntegerField(required=False)  # Frontend sends this
    student_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    # Validate and convert course_id to instance
    def validate_course(self, value):
        try:
            return Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course with the given ID does not exist.")

    # Validate and convert batch_id to instance
    def validate_batch(self, value):
        try:
            return Batch.objects.get(id=value)
        except Batch.DoesNotExist:
            raise serializers.ValidationError("Batch with the given ID does not exist.")

    def validate(self, data):
        criteria = data.get("criteria")

        # Validate for 'course' criteria
        if criteria == "course":
            if not data.get("course"):
                raise serializers.ValidationError({"course": "This field is required for 'course' criteria."})

        # Validate for 'batch' criteria
        if criteria == "batch":
            if not data.get("batch"):
                raise serializers.ValidationError({"batch": "This field is required for 'batch' criteria."})

        # Validate for 'manual' criteria
        if criteria == "student":
            if not data.get("student_ids"):
                raise serializers.ValidationError({"student_ids": "This field is required for 'student' criteria."})

        return data
