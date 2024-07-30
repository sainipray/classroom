import base64
import datetime

import pyotp
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import salted_hmac
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    int_to_base36,
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)


class OTPManager:
    def __init__(self):
        self.token_generator = PasswordResetTokenGenerator()

    def generate_token(self, user):
        token = self.token_generator.make_token(user)
        uid_64 = urlsafe_base64_encode(force_bytes(user.phone_number))
        user_token = f"{token}${uid_64}"
        secret = base64.b32encode(user_token.encode())
        return secret.decode()

    def validate_token(self, secret):
        user_token = base64.b32decode(secret.encode()).decode()
        token, uid_64 = user_token.split("$")
        phone_number = force_str(urlsafe_base64_decode(uid_64))
        return phone_number

    def get_totp(self, user):
        secret = self.generate_token(user)
        totp = pyotp.TOTP(secret, interval=300)  # 5 minute interval
        OTP = totp.now()
        return {"token": secret, "OTP": OTP}

    def verify_totp(self, secret, otp, valid_window=1):
        totp = pyotp.TOTP(secret, interval=300)  # 5 minute interval
        return totp.verify(otp, valid_window=valid_window)

    def _make_token_with_timestamp(self, user, timestamp, legacy=False):
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.token_generator.key_salt,
            self._make_hash_value(user, timestamp),
            secret=self.token_generator.secret,
        ).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(self, user, timestamp):
        current_timestamp = datetime.datetime.now()
        return str(user.pk) + user.password + str(current_timestamp) + str(timestamp)
