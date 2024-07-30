# settings/swagger_docs.py
from drf_yasg import openapi

# Define response schema for settings
settings_response_schema = openapi.Response(
    description="Successful response with settings data",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "group_study": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Enable Group Study"
            ),
            "parent_login": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Enable Parent Login"
            ),
            "configure_grading": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Configure Grading"
            ),
            # Security Settings
            "anti_piracy_watermark_videos": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Enable watermark on store videos",
            ),
            "anti_piracy_watermark_live": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Enable watermark on live class videos",
            ),
            "anti_piracy_watermark_image": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Enable image watermark"
            ),
            "anti_piracy_watermark_image_upload": openapi.Schema(
                type=openapi.TYPE_STRING, description="Upload custom watermark image"
            ),
            "safety_net_check": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Enable safety net check"
            ),
            "device_restriction": openapi.Schema(
                type=openapi.TYPE_STRING, description="Device restriction policy"
            ),
            # Live Class Settings
            "allow_on_desktop": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Allow live classes on desktop"
            ),
            "show_recorded_class_on_web": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Show recorded class on web"
            ),
            "attendance_criteria": openapi.Schema(
                type=openapi.TYPE_INTEGER, description="Attendance criteria in %"
            ),
            # Payment Gateway Settings
            "razorpay_api_base_url": openapi.Schema(
                type=openapi.TYPE_STRING, description="Razorpay API Base URL"
            ),
            "razorpay_api_key": openapi.Schema(
                type=openapi.TYPE_STRING, description="Razorpay API Key"
            ),
            "razorpay_api_secret": openapi.Schema(
                type=openapi.TYPE_STRING, description="Razorpay API Secret"
            ),
            # SMS Gateway (DLT) Settings
            "sms_gateway_api_base_url": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMS Gateway API Base URL"
            ),
            "sms_gateway_api_key": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMS Gateway API Key"
            ),
            "sms_gateway_route": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMS Gateway Route"
            ),
            "sms_gateway_sender_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMS Gateway Sender ID"
            ),
            "sms_gateway_templates": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMS Gateway Templates"
            ),
            # SMTP Email Settings
            "smtp_mail_host": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMTP Mail Host"
            ),
            "smtp_mail_port": openapi.Schema(
                type=openapi.TYPE_INTEGER, description="SMTP Mail Port"
            ),
            "smtp_mail_username": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMTP Mail Username"
            ),
            "smtp_mail_password": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMTP Mail Password"
            ),
            "smtp_mail_from_address": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMTP Mail From Address"
            ),
            "smtp_mail_from_name": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMTP Mail From Name"
            ),
            "smtp_mail_bcc_list": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMTP Mail BCC List"
            ),
            # MeritHub API Settings
            "merithub_api_base_url": openapi.Schema(
                type=openapi.TYPE_STRING, description="MeritHub API Base URL"
            ),
            "merithub_client_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="MeritHub Client ID"
            ),
            "merithub_client_secret": openapi.Schema(
                type=openapi.TYPE_STRING, description="MeritHub Client Secret"
            ),
            # Firebase Settings
            "firebase_api_key": openapi.Schema(
                type=openapi.TYPE_STRING, description="Firebase API Key"
            ),
            "firebase_auth_domain": openapi.Schema(
                type=openapi.TYPE_STRING, description="Firebase Auth Domain"
            ),
            "firebase_project_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="Firebase Project ID"
            ),
            "firebase_storage_bucket": openapi.Schema(
                type=openapi.TYPE_STRING, description="Firebase Storage Bucket"
            ),
            "firebase_messaging_sender_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="Firebase Messaging Sender ID"
            ),
            "firebase_app_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="Firebase App ID"
            ),
            # Tax Setup
            "tax_setup": openapi.Schema(
                type=openapi.TYPE_STRING, description="Tax Setup"
            ),
            # SMS & Email Schedulers
            "sms_email_schedulers": openapi.Schema(
                type=openapi.TYPE_STRING, description="SMS & Email Schedulers"
            ),
            # Live Chat Settings
            "live_chat_create_group": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Allow students to create groups and chat",
            ),
            "live_chat_document_share": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Allow document sharing"
            ),
            "live_chat_image_share": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Allow image sharing"
            ),
            "live_chat_audio_share": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Allow audio file sharing"
            ),
        },
    ),
)

# Define request body schema for updating settings
update_settings_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "group_study": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Enable Group Study"
        ),
        "parent_login": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Enable Parent Login"
        ),
        "configure_grading": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Configure Grading"
        ),
        "anti_piracy_watermark_videos": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Enable watermark on store videos"
        ),
        "anti_piracy_watermark_live": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="Enable watermark on live class videos",
        ),
        "anti_piracy_watermark_image": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Enable image watermark"
        ),
        "anti_piracy_watermark_image_upload": openapi.Schema(
            type=openapi.TYPE_STRING, description="Upload custom watermark image"
        ),
        "safety_net_check": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Enable safety net check"
        ),
        "device_restriction": openapi.Schema(
            type=openapi.TYPE_STRING, description="Device restriction policy"
        ),
        "allow_on_desktop": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Allow live classes on desktop"
        ),
        "show_recorded_class_on_web": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Show recorded class on web"
        ),
        "attendance_criteria": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="Attendance criteria in %"
        ),
        "razorpay_api_base_url": openapi.Schema(
            type=openapi.TYPE_STRING, description="Razorpay API Base URL"
        ),
        "razorpay_api_key": openapi.Schema(
            type=openapi.TYPE_STRING, description="Razorpay API Key"
        ),
        "razorpay_api_secret": openapi.Schema(
            type=openapi.TYPE_STRING, description="Razorpay API Secret"
        ),
        "sms_gateway_api_base_url": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMS Gateway API Base URL"
        ),
        "sms_gateway_api_key": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMS Gateway API Key"
        ),
        "sms_gateway_route": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMS Gateway Route"
        ),
        "sms_gateway_sender_id": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMS Gateway Sender ID"
        ),
        "sms_gateway_templates": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMS Gateway Templates"
        ),
        "smtp_mail_host": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMTP Mail Host"
        ),
        "smtp_mail_port": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="SMTP Mail Port"
        ),
        "smtp_mail_username": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMTP Mail Username"
        ),
        "smtp_mail_password": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMTP Mail Password"
        ),
        "smtp_mail_from_address": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMTP Mail From Address"
        ),
        "smtp_mail_from_name": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMTP Mail From Name"
        ),
        "smtp_mail_bcc_list": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMTP Mail BCC List"
        ),
        "merithub_api_base_url": openapi.Schema(
            type=openapi.TYPE_STRING, description="MeritHub API Base URL"
        ),
        "merithub_client_id": openapi.Schema(
            type=openapi.TYPE_STRING, description="MeritHub Client ID"
        ),
        "merithub_client_secret": openapi.Schema(
            type=openapi.TYPE_STRING, description="MeritHub Client Secret"
        ),
        "firebase_api_key": openapi.Schema(
            type=openapi.TYPE_STRING, description="Firebase API Key"
        ),
        "firebase_auth_domain": openapi.Schema(
            type=openapi.TYPE_STRING, description="Firebase Auth Domain"
        ),
        "firebase_project_id": openapi.Schema(
            type=openapi.TYPE_STRING, description="Firebase Project ID"
        ),
        "firebase_storage_bucket": openapi.Schema(
            type=openapi.TYPE_STRING, description="Firebase Storage Bucket"
        ),
        "firebase_messaging_sender_id": openapi.Schema(
            type=openapi.TYPE_STRING, description="Firebase Messaging Sender ID"
        ),
        "firebase_app_id": openapi.Schema(
            type=openapi.TYPE_STRING, description="Firebase App ID"
        ),
        "tax_setup": openapi.Schema(type=openapi.TYPE_STRING, description="Tax Setup"),
        "sms_email_schedulers": openapi.Schema(
            type=openapi.TYPE_STRING, description="SMS & Email Schedulers"
        ),
        "live_chat_create_group": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="Allow students to create groups and chat",
        ),
        "live_chat_document_share": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Allow document sharing"
        ),
        "live_chat_image_share": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Allow image sharing"
        ),
        "live_chat_audio_share": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Allow audio file sharing"
        ),
    },
)
