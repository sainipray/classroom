from django.db import transaction
from rest_framework import serializers

from apps.batch.models import Enrollment, Batch
from apps.user.models import CustomUser, Roles, Student
from apps.user.serializers import StudentUserSerializer


# class BatchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Batch
#         fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    students = serializers.ListField(
        child=serializers.IntegerField(),  # Assuming student IDs are integers
        write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ['batch', 'students', 'is_approved']

    def validate(self, attrs):
        batch = attrs.get('batch')
        student_ids = attrs.get('students')

        if not batch or not student_ids:
            raise serializers.ValidationError("Batch ID and student IDs are required.")

        if not CustomUser.objects.filter(id__in=student_ids).exists():
            raise serializers.ValidationError("One or more student IDs do not exist.")

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        students = validated_data.pop('students')
        enrollments = []
        for student_id in students:
            enrollment, created = Enrollment.objects.get_or_create(
                batch=validated_data['batch'],
                student_id=student_id,
                is_approved=True,
                approved_by=request.user
            )
            enrollments.append(enrollment)

        return enrollments


class RetrieveEnrollmentSerializer(serializers.ModelSerializer):
    # batch = BatchSerializer(read_only=True)
    student = serializers.StringRelatedField()  # Adjust if you need more details
    approved_by = serializers.StringRelatedField()  # Adjust if you need more details

    class Meta:
        model = Enrollment
        fields = '__all__'


class ListEnrollmentSerializer(serializers.ModelSerializer):
    approved_by = serializers.ReadOnlyField(source='approved_by.full_name')  # Adjust if you need more details

    class Meta:
        model = Enrollment
        fields = '__all__'


class BatchStudentUserSerializer(StudentUserSerializer):
    batch = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all(), write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone_number', 'full_name', 'role', 'is_active', 'date_joined', 'student', 'batch']

    def create(self, validated_data):
        batch = validated_data.pop('batch')  # Extract the batch from validated data
        with transaction.atomic():
            user = CustomUser.objects.create_user(role=Roles.STUDENT, **validated_data)
            student = Student.objects.create(user=user)

            # Create enrollment for the newly created student
            Enrollment.objects.create(batch=batch, student=user)

            return user
