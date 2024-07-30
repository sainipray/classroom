# settings/views.py
from constance import config
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import IsAdmin

from .schema_definitions import settings_response_schema, update_settings_request_schema


class GetSettingsAPIView(APIView):
    permission_classes = [IsAdmin]  # Only admins can view settings

    @settings_response_schema
    def get(self, request, *args, **kwargs):
        settings = {
            "group_study": config.GROUP_STUDY,
            "parent_login": config.PARENT_LOGIN,
            "configure_grading": config.CONFIGURE_GRADING,
            "anti_piracy_watermark_videos": config.ANTI_PIRACY_WATERMARK_VIDEOS,
            "anti_piracy_watermark_live": config.ANTI_PIRACY_WATERMARK_LIVE,
            "anti_piracy_watermark_image": config.ANTI_PIRACY_WATERMARK_IMAGE,
            "anti_piracy_watermark_image_upload": config.ANTI_PIRACY_WATERMARK_IMAGE_UPLOAD,
            "safety_net_check": config.SAFETY_NET_CHECK,
            "device_restriction": config.DEVICE_RESTRICTION,
            "allow_on_desktop": config.ALLOW_ON_DESKTOP,
            "show_recorded_class_on_web": config.SHOW_RECORDED_CLASS_ON_WEB,
            "attendance_criteria": config.ATTENDANCE_CRITERIA,
            "razorpay_api_base_url": config.RAZORPAY_API_BASE_URL,
            "razorpay_api_key": config.RAZORPAY_API_KEY,
            "razorpay_api_secret": config.RAZORPAY_API_SECRET,
            "sms_gateway_api_base_url": config.SMS_GATEWAY_API_BASE_URL,
            "sms_gateway_api_key": config.SMS_GATEWAY_API_KEY,
            "sms_gateway_route": config.SMS_GATEWAY_ROUTE,
            "sms_gateway_sender_id": config.SMS_GATEWAY_SENDER_ID,
            "sms_gateway_templates": config.SMS_GATEWAY_TEMPLATES,
            "smtp_mail_host": config.SMTP_MAIL_HOST,
            "smtp_mail_port": config.SMTP_MAIL_PORT,
            "smtp_mail_username": config.SMTP_MAIL_USERNAME,
            "smtp_mail_password": config.SMTP_MAIL_PASSWORD,
            "smtp_mail_from_address": config.SMTP_MAIL_FROM_ADDRESS,
            "smtp_mail_from_name": config.SMTP_MAIL_FROM_NAME,
            "smtp_mail_bcc_list": config.SMTP_MAIL_BCC_LIST,
            "merithub_api_base_url": config.MERITHUB_API_BASE_URL,
            "merithub_client_id": config.MERITHUB_CLIENT_ID,
            "merithub_client_secret": config.MERITHUB_CLIENT_SECRET,
            "firebase_api_key": config.FIREBASE_API_KEY,
            "firebase_auth_domain": config.FIREBASE_AUTH_DOMAIN,
            "firebase_project_id": config.FIREBASE_PROJECT_ID,
            "firebase_storage_bucket": config.FIREBASE_STORAGE_BUCKET,
            "firebase_messaging_sender_id": config.FIREBASE_MESSAGING_SENDER_ID,
            "firebase_app_id": config.FIREBASE_APP_ID,
            "tax_setup": config.TAX_SETUP,
            "sms_email_schedulers": config.SMS_EMAIL_SCHEDULERS,
            "live_chat_create_group": config.LIVE_CHAT_CREATE_GROUP,
            "live_chat_document_share": config.LIVE_CHAT_DOCUMENT_SHARE,
            "live_chat_image_share": config.LIVE_CHAT_IMAGE_SHARE,
            "live_chat_audio_share": config.LIVE_CHAT_AUDIO_SHARE,
        }
        return Response(settings, status=status.HTTP_200_OK)


class UpdateSettingsAPIView(APIView):
    permission_classes = [IsAdmin]  # Only admins can update settings

    @update_settings_request_schema
    def post(self, request, *args, **kwargs):
        data = request.data
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return Response(
            {"message": "Settings updated successfully"}, status=status.HTTP_200_OK
        )
