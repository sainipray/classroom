from rest_framework import serializers

from apps.batch.models import Attendance, Batch, LiveClass


# class BatchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Batch
#         fields = '__all__'
#
#
# class LiveClassSerializer(serializers.ModelSerializer):
#     batch = BatchSerializer(read_only=True)
#
#     class Meta:
#         model = LiveClass
#         fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()  # Adjust if you need more details
    # live_class = LiveClassSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'


class RetrieveAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()  # Adjust if you need more details
    # live_class = LiveClassSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'


class ListAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()  # Adjust if you need more details
    # live_class = LiveClassSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'
