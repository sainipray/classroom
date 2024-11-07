from django.core.exceptions import ValidationError
from django.db import transaction
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from config.sms.otp import OTPManager
from .models import CustomUser, Manager, Instructor, Roles
from .models import Student


class SignupSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(region="IN")

    class Meta:
        model = CustomUser
        fields = ["full_name", "email", "phone_number"]

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError("Email is already in use.")
        return value

    def validate_phone_number(self, value):
        user = CustomUser.objects.filter(phone_number=value).first()
        if user:
            if not user.is_active:
                raise ValidationError(
                    "Your account is disabled. Please contact the administrator."
                )
            else:
                raise ValidationError("Phone number is already in use.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        Student.objects.create(user=user)
        return user


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField()
    reference_key = serializers.CharField()

    # push_notification_token = serializers.CharField(required=False)
    # device_id = serializers.CharField(required=False)

    def validate(self, attrs):
        otp = attrs["otp"]
        reference_key = attrs["reference_key"]
        otp_manager = OTPManager()
        phone_number = otp_manager.validate_token(reference_key)
        response = otp_manager.verify_totp(reference_key, otp)
        if not response:
            raise serializers.ValidationError(
                {"otp": "Invalid OTP or Expired, Resend again"}
            )
        attrs["phone_number"] = phone_number
        return attrs


class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(region='IN')

    def validate_phone_number(self, value):
        try:
            user = CustomUser.objects.get(phone_number=value)
        except CustomUser.DoesNotExist:
            raise ValidationError("User with this phone number does not exist.")

        if not user.is_active:
            raise ValidationError("This account is inactive. Please contact the admin for activation.")

        return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "full_name",
            "email",
            "phone_number",
            'role'
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(region="IN")

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'phone_number', 'role', 'is_active', 'date_joined']

    def validate_phone_number(self, value):
        # Check if the phone number already exists in the database
        if self.instance:
            # If updating, exclude the current user from the check
            user = CustomUser.objects.filter(phone_number=value).exclude(id=self.instance.id).first()
            if user:
                raise ValidationError("Phone number is already in use.")
        else:
            # If creating, just check for existence
            if CustomUser.objects.filter(phone_number=value).exists():
                raise ValidationError("Phone number is already in use.")
        return value

    def create(self, validated_data):
        # Create user based on role
        role = validated_data.pop('role')
        user = CustomUser.objects.create(**validated_data, role=role)

        # Create the corresponding role model based on the user's role
        if role == Roles.MANAGER:
            Manager.objects.create(user=user)
        elif role == Roles.INSTRUCTOR:
            Instructor.objects.create(user=user)
        # Admin role doesn't require a separate model, so no need to create anything for admin
        return user


class StudentSerializer(serializers.ModelSerializer):
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


class StudentUserSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone_number', 'full_name', 'role', 'is_active', 'date_joined', 'student']

    def validate_email(self, value):
        # Check if the email already exists in the database
        if self.instance:
            # If updating, exclude the current user from the check
            if CustomUser.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise ValidationError("Email is already in use.")
        else:
            # If creating, just check for existence
            if CustomUser.objects.filter(email=value).exists():
                raise ValidationError("Email is already in use.")
        return value

    def validate_phone_number(self, value):
        # Check if the phone number already exists in the database
        if self.instance:
            # If updating, exclude the current user from the check
            user = CustomUser.objects.filter(phone_number=value).exclude(id=self.instance.id).first()
            if user:
                if not user.is_active:
                    raise ValidationError("Your account is disabled. Please contact the administrator.")
                raise ValidationError("Phone number is already in use.")
        else:
            # If creating, just check for existence
            if CustomUser.objects.filter(phone_number=value).exists():
                raise ValidationError("Phone number is already in use.")
        return value

    def create(self, validated_data):
        with transaction.atomic():
            user = CustomUser.objects.create_user(role=Roles.STUDENT, **validated_data)
            Student.objects.create(user=user)
            return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in ['full_name', 'email', 'phone_number']:
                setattr(instance, attr, value)
        instance.save()
        return instance
