import uuid
import io
from minio import Minio
from minio.error import S3Error
from app.config import settings

_client: Minio | None = None


def get_minio() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
    return _client


def upload_vehicle_photo(file_bytes: bytes, content_type: str, ext: str) -> str:
    client = get_minio()
    bucket = settings.minio_bucket

    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        _set_public_policy(client, bucket)
    except S3Error:
        pass

    object_name = f"vehicles/{uuid.uuid4().hex}{ext}"
    client.put_object(
        bucket,
        object_name,
        io.BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=content_type,
    )

    scheme = "https" if settings.minio_secure else "http"
    return f"{scheme}://{settings.minio_endpoint}/{bucket}/{object_name}"


def _set_public_policy(client: Minio, bucket: str) -> None:
    import json
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket}/*"],
            }
        ],
    }
    client.set_bucket_policy(bucket, json.dumps(policy))
