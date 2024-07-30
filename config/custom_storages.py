from constance import config
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class S3Storage(S3Boto3Storage):
    bucket_name = "your-aws-bucket-name"
    region_name = "your-aws-region"
    custom_domain = f"{bucket_name}.s3.amazonaws.com"


class LocalStorage(FileSystemStorage):
    location = "media"
    base_url = "/media/"


def get_storage_class():
    storage_backend = config.DEFAULT_STORAGE_BACKEND.lower()
    if storage_backend == "s3":
        return S3Storage()
    else:
        return LocalStorage()
