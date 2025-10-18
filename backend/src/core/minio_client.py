from minio import Minio
from functools import lru_cache
from .config import settings

@lru_cache
def get_minio_client() -> Minio:
    """Dependency for injecting a configured MinIO client."""
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )

    # Ensure the bucket exists
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)

    return client
