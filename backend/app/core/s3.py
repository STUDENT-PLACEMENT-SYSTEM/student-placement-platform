import boto3
from botocore.client import Config
from backend.app.core.config import settings

def get_s3_client():
    protocol = "https" if settings.MINIO_USE_SSL else "http"
    endpoint_url = f"{protocol}://{settings.MINIO_ENDPOINT}"
    
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1"
    )

def ensure_buckets_exist():
    try:
        s3 = get_s3_client()
        buckets = [settings.MINIO_BUCKET_RESUMES, settings.MINIO_BUCKET_JDS, settings.MINIO_BUCKET_OFFERS]
        existing = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
        for b in buckets:
            if b not in existing:
                s3.create_bucket(Bucket=b)
    except Exception as e:
        print(f"[Warning] Could not initialize MinIO buckets: {e}")
