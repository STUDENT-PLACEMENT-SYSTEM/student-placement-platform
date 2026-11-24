from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Student Placement Analytics Platform"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "super-secret-random-32-byte-hex-key-here-for-jwt-signing"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/placement_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # S3 / MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET_RESUMES: str = "placement-resumes"
    MINIO_BUCKET_JDS: str = "placement-jds"
    MINIO_BUCKET_OFFERS: str = "placement-offers"
    MINIO_USE_SSL: bool = False
    
    # AI / LLM
    OPENAI_API_KEY: Optional[str] = "mock-key"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
