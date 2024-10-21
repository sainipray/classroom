from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.batch import models
from apps.batch.models import LiveClass, Batch


# class BatchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Batch
#         fields = '__all__'


class LiveClassSerializer(serializers.ModelSerializer):
    # batch = BatchSerializer(read_only=True)

    class Meta:
        model = LiveClass
        fields = '__all__'


class CreateLiveClassSerializer(serializers.Serializer):
    batch = serializers.IntegerField()
    title = serializers.CharField(required=True, max_length=255)
    start_time = serializers.DateTimeField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, default="This is a scheduled class.")
    enable_recording = serializers.BooleanField(required=False, default=False)

    def validate_batch(self, value):
        try:
            batch = Batch.objects.get(id=value)
            return batch
        except Batch.DoesNotExist:
            raise serializers.ValidationError("Batch with id {} does not exist".format(value))

    def validate(self, data):
        now = timezone.now()
        start_time = data.get('start_time')
        batch = data['batch']
        enrolled_student_count = models.Enrollment.objects.filter(batch=batch, is_approved=True).count()
        if not enrolled_student_count:
            raise serializers.ValidationError("No student is enrolled in this batch")

        # Determine status and validate start_time
        if start_time:
            if start_time <= now:
                raise serializers.ValidationError({"start_time": "start_time must be a future date and time."})
            data['status'] = 'up'  # Upcoming
            data['startTime'] = start_time.isoformat()
        else:
            data['status'] = 'lv'  # Live
            data['startTime'] = now.isoformat()

        # Set endDate to one hour after startTime
        end_time = datetime.fromisoformat(data['startTime']) + timedelta(hours=1)
        data['endDate'] = end_time.isoformat()

        # Set default values
        data['type'] = 'oneTime'
        data['layout'] = 'CR'
        data['duration'] = 60  # Duration in minutes
        data['lang'] = 'en'
        data['timeZoneId'] = 'Asia/Kolkata'
        data['access'] = 'private'
        data['login'] = False  # Adjust if needed

        # Set recording options
        data['recording'] = {
            'record': data.get('enable_recording', False),
            'autoRecord': False,
            'recordingControl': True
        }

        # Participant control default settings
        data['participantControl'] = {
            'write': False,
            'audio': False,
            'video': False
        }

        return data


class RetrieveLiveClassSerializer(serializers.ModelSerializer):
    # batch = BatchSerializer(read_only=True)

    class Meta:
        model = LiveClass
        fields = '__all__'


class ListLiveClassSerializer(serializers.ModelSerializer):
    # batch = BatchSerializer(read_only=True)

    class Meta:
        model = LiveClass
        fields = '__all__'
