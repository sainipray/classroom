# settings/views.py
from constance import config
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import IsAdmin
from .enums import SettingKeys


class GetSettingsAPIView(APIView):
    # permission_classes = [IsAdmin]  # Only admins can view settings

    # @settings_response_schema
    def get(self, request, *args, **kwargs):
        settings = {key.value: getattr(config, key.value, None) for key in SettingKeys}
        return Response(settings, status=status.HTTP_200_OK)


class UpdateSettingsAPIView(APIView):
    permission_classes = [IsAdmin]  # Only admins can update settings

    # @update_settings_request_schema
    def post(self, request, *args, **kwargs):
        data = request.data

        # Validate keys
        invalid_keys = [key for key in data if key not in SettingKeys.values()]
        if invalid_keys:
            return Response(
                {"error": f"Invalid keys provided: {', '.join(invalid_keys)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update only allowed keys
        for key, value in data.items():
            # Check if the key exists in CONSTANCE_CONFIG
            # if key in config.CONSTANCE_CONFIG:
            #     setattr(config, key, value)
            if key in list(settings.CONSTANCE_CONFIG.keys()):
                # Update the config value
                setattr(config, key, value)

        return Response(
            {"message": "Settings updated successfully"}, status=status.HTTP_200_OK
        )
