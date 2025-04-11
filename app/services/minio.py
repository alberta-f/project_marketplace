from uuid import uuid4

from boto3 import client as boto3_client

from app.core.config import config


class MinioService:
    def __init__(self):
        self.client = None
        self.bucket = config.minio.bucket
        self.endpoint = config.minio.endpoint

    def _get_boto3_client(self):
        if self.client is None:
            self.client = boto3_client(
            "s3",
            endpoint_url=f"http://{self.endpoint}",
            aws_access_key_id=config.minio.access_key,
            aws_secret_access_key=config.minio.secret_key.get_secret_value(),
            )
        return self.client

    def upload_image(self, file_data: bytes, filename: str, content_type: str = "image/jpeg"):
        unique_name = f"{uuid4()}_{filename}"

        client = self._get_boto3_client()
        client.put_object(
            Bucket=self.bucket,
            Key=unique_name,
            Body=file_data,
            ContentType=content_type,
        )

        return f"http://{self.endpoint}/{self.bucket}/{unique_name}"
