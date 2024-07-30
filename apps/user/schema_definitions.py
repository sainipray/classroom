# accounts/swagger_docs.py
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .serializers import (
    LoginSerializer,
    SignupSerializer,
    StudentProfileSerializer,
    VerifyOTPSerializer,
)

# Define response schema directly without using serializers
register_api_response_schema = openapi.Response(
    description="OTP sent to phone number. Reference key returned.",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "message": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Please verify OTP sent to your phone number",
            ),
            "reference_key": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Reference key for OTP verification",
            ),
        },
    ),
)

register_api_view = swagger_auto_schema(
    operation_description="Register a new user and send OTP to the phone number",
    request_body=SignupSerializer,
    responses={200: register_api_response_schema, 400: "Bad Request"},
)

phone_otp_verify_api_response_schema = openapi.Response(
    description="Phone verified. JWT tokens returned.",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "refresh": openapi.Schema(
                type=openapi.TYPE_STRING, description="Refresh token"
            ),
            "access": openapi.Schema(
                type=openapi.TYPE_STRING, description="Access token"
            ),
            "message": openapi.Schema(
                type=openapi.TYPE_STRING, description="Phone verified"
            ),
            "role": openapi.Schema(type=openapi.TYPE_STRING, description="User role"),
        },
    ),
)

phone_otp_verify_api_view = swagger_auto_schema(
    operation_description="Verify OTP sent to the phone number",
    request_body=VerifyOTPSerializer,
    responses={
        200: phone_otp_verify_api_response_schema,
        400: "Invalid OTP or bad request",
    },
)

login_api_response_schema = openapi.Response(
    description="OTP sent to phone number. Reference key returned.",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "message": openapi.Schema(
                type=openapi.TYPE_STRING, description="OTP sent to your phone number"
            ),
            "reference_key": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Reference key for OTP verification",
            ),
        },
    ),
)

login_api_view = swagger_auto_schema(
    operation_description="Login an existing user and send OTP to the phone number",
    request_body=LoginSerializer,
    responses={200: login_api_response_schema, 400: "Bad Request"},
)


# Define response schema for student profile
student_profile_response_schema = openapi.Response(
    description="Successful response with student profile data",
    schema=StudentProfileSerializer,
)

student_profile_api_view = swagger_auto_schema(
    operation_description="Retrieve and update the authenticated student's profile",
    responses={
        200: student_profile_response_schema,
        400: "Bad Request",
        401: "Unauthorized",
    },
)
