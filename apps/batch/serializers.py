from rest_framework import serializers

from .models import Subject, Batch, Enrollment, LiveClass, Attendance, StudyMaterial
from ..user.serializers import CustomUserSerializer


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class RetrieveSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class ListSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'


class RetrieveBatchSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    created_by = CustomUserSerializer()

    class Meta:
        model = Batch
        fields = '__all__'


class ListBatchSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    created_by = CustomUserSerializer()

    class Meta:
        model = Batch
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    student = serializers.StringRelatedField()  # Adjust if you need more details
    approved_by = serializers.StringRelatedField()  # Adjust if you need more details

    class Meta:
        model = Enrollment
        fields = '__all__'


class RetrieveEnrollmentSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    student = serializers.StringRelatedField()  # Adjust if you need more details
    approved_by = serializers.StringRelatedField()  # Adjust if you need more details

    class Meta:
        model = Enrollment
        fields = '__all__'


class ListEnrollmentSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    student = serializers.StringRelatedField()  # Adjust if you need more details
    approved_by = serializers.StringRelatedField()  # Adjust if you need more details

    class Meta:
        model = Enrollment
        fields = '__all__'


class LiveClassSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)

    class Meta:
        model = LiveClass
        fields = '__all__'


class RetreiveLiveClassSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)

    class Meta:
        model = LiveClass
        fields = '__all__'


class ListLiveClassSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)

    class Meta:
        model = LiveClass
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()  # Adjust if you need more details
    live_class = LiveClassSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'


class RetrieveAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()  # Adjust if you need more details
    live_class = LiveClassSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'


class ListAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()  # Adjust if you need more details
    live_class = LiveClassSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'


class StudyMaterialSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    live_class_recording = LiveClassSerializer(read_only=True)

    class Meta:
        model = StudyMaterial
        fields = '__all__'


class RetrieveStudyMaterialSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    live_class_recording = LiveClassSerializer(read_only=True)

    class Meta:
        model = StudyMaterial
        fields = '__all__'


class ListStudyMaterialSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    live_class_recording = LiveClassSerializer(read_only=True)

    class Meta:
        model = StudyMaterial
        fields = '__all__'
