import json

import requests
from constance import config

from config.sms.otp import OTPManager

# API KEY = NmQzNTZkNTQ1MjZlNDg1NDRiNDc1MTczNTU2MTRlN2E=
# Sender = BALUJC
LOGIN_OTP_KEY = "login_otp_key"
SIGNUP_OTP_KEY = "signup_otp_key"

MESSAGES = {
    SIGNUP_OTP_KEY: "{otp} is Your Registration OTP for Baluja Classes. It is valid for 5 minutes. "
    "Please do not share it with anyone. Team Baluja Classes",
    LOGIN_OTP_KEY: "{otp} is Your Login OTP for Baluja Classes. It is valid for 5 minutes. "
    "Please do not share it with anyone. Team Baluja Classes",
}


class SMSManager:
    def __init__(self, user, apikey=None, sender=None):
        self.user = user
        self.apikey = apikey or config.TEXT_LOCAL_SMS_APIKEY
        self.sender = sender or config.TEXT_LOCAL_SMS_SENDER

    def send_sms(self, numbers, message):
        url = "https://api.textlocal.in/send/"
        data = {
            "apikey": self.apikey,
            "numbers": numbers,
            "message": message,
            "sender": self.sender,
        }
        response = requests.post(url, data=data)
        return response.text

    def _send_otp(self, number, message):
        otp_manager = OTPManager()
        data = otp_manager.get_totp(self.user)
        otp = data["OTP"]
        message = message.format(otp=otp)
        response = json.loads(self.send_sms(number, message))
        if response["status"] == "success":
            print("OTP sent successfully!")
        else:
            print("Failed to send OTP.")
        return data

    def send_otp(self, number, otp_key):
        return self._send_otp(number, MESSAGES[otp_key])
