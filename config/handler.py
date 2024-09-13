from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import set_rollback


def custom_exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait

        if isinstance(exc.detail, (list, dict)):
            output = exc.detail
        else:
            output = {"non_field_errors": exc.detail}
        error = {}
        for field, value in output.items():
            if isinstance(value, list):
                value = value[0]
            error[field] = value
        data = {"error": error, "status": False}
        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)
    return None
