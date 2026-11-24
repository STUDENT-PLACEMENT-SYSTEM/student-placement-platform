import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import boto3
from botocore.client import Config as BotoConfig


class WorkerSettings(BaseSettings):
    ENVIRONMENT: str = Field(default="development")
    
    # Database Settings
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="placement_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/placement_db"
    )
    
    # Redis Settings
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # MinIO / S3 Settings
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ROOT_USER: str = Field(default="minioadmin")
    MINIO_ROOT_PASSWORD: str = Field(default="minioadmin")
    MINIO_BUCKET_RESUMES: str = Field(default="placement-resumes")
    MINIO_BUCKET_JDS: str = Field(default="placement-jds")
    MINIO_BUCKET_OFFERS: str = Field(default="placement-offers")
    MINIO_USE_SSL: bool = Field(default=False)
    
    # OpenAI / AI Agent Settings
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    EMBEDDING_DIMENSION: int = Field(default=1536)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = WorkerSettings()


def get_asyncpg_dsn() -> str:
    """Return clean asyncpg connection DSN string (converting postgresql+asyncpg:// to postgresql://)."""
    dsn = settings.DATABASE_URL
    if dsn.startswith("postgresql+asyncpg://"):
        dsn = "postgresql://" + dsn[len("postgresql+asyncpg://"):]
    return dsn


def get_s3_client():
    """Return boto3 S3 client configured for MinIO."""
    endpoint_url = settings.MINIO_ENDPOINT
    if not endpoint_url.startswith("http://") and not endpoint_url.startswith("https://"):
        proto = "https" if settings.MINIO_USE_SSL else "http"
        endpoint_url = f"{proto}://{endpoint_url}"
        
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
        config=BotoConfig(signature_version="s3v4"),
        region_name="us-east-1"
    )
