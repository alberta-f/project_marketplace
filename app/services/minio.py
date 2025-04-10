from uuid import uuid4

from boto3 import client as boto3_client

from app.core.config import config


class MinioService:
    def __init__(self):
        self.client = boto3_client(
            "s3",
            endpoint_url=f"http://{config.minio.endpoint}",
            aws_access_key_id=config.minio.access_key,
            aws_secret_access_key=config.minio.secret_key,
        )
        self.bucket = config.minio.bucket
        self.endpoint = config.minio.endpoint

    def upload_image(self, file_data: bytes, filename: str, content_type: str = "image/jpeg"):
        unique_name = f"{uuid4()}_{filename}"

        self.client.put_object(
            Bucket=self.bucket,
            Key=unique_name,
            Body=file_data,
            ContentType=content_type,
        )

        return f"http://{self.endpoint}/{self.bucket}/{unique_name}"
