import uuid
from typing import Any
import aioboto3
from botocore.config import Config
from app.core.config import settings

# Initialize session using credentials from settings
_session = aioboto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION,
)

ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

def generate_s3_key(doctor_id: uuid.UUID, filename: str) -> str:
    """Generates a unique, collision-proof S3 storage path."""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    return f"records/{doctor_id}/{uuid.uuid4()}.{ext}"

async def upload_to_s3(file_obj: Any, s3_key: str, content_type: str) -> None:
    """Streams file bytes directly to MinIO/S3 without loading into memory."""
    # # type: ignore tells Pylance to stop analyzing this specific context manager line
    async with _session.client(
        "s3",
        endpoint_url=settings.AWS_ENDPOINT_URL,
        config=Config(signature_version="s3v4")
    ) as s3:  # type: ignore
        await s3.upload_fileobj(
            Fileobj=file_obj,
            Bucket=getattr(settings, "S3_BUCKET", "medicosync-records-prod"),
            Key=s3_key,
            ExtraArgs={"ContentType": content_type}
        )

async def generate_presigned_url(s3_key: str, expiry: int = 3600) -> str:
    """Generates a time-limited read-only access URL for a private file."""
    async with _session.client(
        "s3",
        endpoint_url=settings.AWS_ENDPOINT_URL,
        config=Config(signature_version="s3v4")
    ) as s3:  # type: ignore
        url: str = await s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": getattr(settings, "S3_BUCKET", "medicosync-records-prod"),
                "Key": s3_key
            },
            ExpiresIn=expiry
        )
        return url

async def delete_from_s3(s3_key: str) -> None:
    """Permanently removes a file from S3/MinIO storage."""
    async with _session.client(
        "s3",
        endpoint_url=settings.AWS_ENDPOINT_URL,
        config=Config(signature_version="s3v4")
    ) as s3:  # type: ignore
        await s3.delete_object(
            Bucket=getattr(settings, "S3_BUCKET", "medicosync-records-prod"),
            Key=s3_key
        )
