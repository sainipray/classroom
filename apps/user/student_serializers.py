from rest_framework import serializers

from .models import CustomUser
from .models import Student


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'about', 'profile_photo', 'mother_name', 'father_name',
            'occupation', 'parent_mobile_number', 'parent_email', 'parent_profile_photo',
            'date_of_birth', 'gender', 'nationality', 'blood_group', 'permanent_address',
            'permanent_address_pincode', 'correspondence_address', 'correspondence_address_pincode',
            'school_name', 'college_name', 'marks_x', 'x_result', 'marks_xii', 'xii_result',
            'marks_college', 'college_result'
        ]

    def update(self, instance, validated_data):
        # Update the Student fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class StudentUserProfileSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone_number', 'full_name', 'role', 'is_active', 'date_joined', 'student']
