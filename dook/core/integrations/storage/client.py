import logging
from datetime import datetime

from boto3 import client
from botocore.exceptions import ClientError
from django.conf import settings

from dook.core.integrations.storage.exceptions import StorageServiceInternalException


class S3ApiClient:
    def __init__(self):
        self.boto3_client = client(
            "s3",
            region_name=settings.REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.logger = logging.getLogger("s3-bucket")

    def upload_image(self, image_object, filename=None):
        if not filename:
            filename = self.generate_filename(type="image")

        try:
            self.boto3_client.upload_fileobj(
                image_object,
                settings.BUCKET_NAME,
                filename,
                ExtraArgs={"ContentType": "image/jpeg", "ACL": "public-read"},
            )
        except ClientError as e:
            self.logger.error(e)
            raise StorageServiceInternalException
        else:
            self.logger.info(f"Uploaded image to s3 bucket, image name: {filename}.")

    def get_object_url(self, object_name):
        """Generate a presigned URL to share an S3 object

        :param bucket_name: string
        :param object_name: string
        :return: Presigned URL as string. If error, returns None.
        """
        # Generate an URL for the S3 object
        url = f"https://{settings.BUCKET_NAME}.s3.amazonaws.com/{object_name}"

        return url

    def generate_filename(self, type="file"):
        time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{type}_{time_stamp}"
        return filename
