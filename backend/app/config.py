"""
ChunkScope Configuration Settings
Uses pydantic-settings for environment variable parsing
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App
    app_name: str = "ChunkScope"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = Field(default="development", description="development | staging | production")
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = Field(
        ...,
        description="PostgreSQL connection string"
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10
    
    # Redis (for Celery and caching)
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT Auth
    jwt_secret_key: str = Field(
        ...,
        description="Secret key for JWT signing"
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # Cohere
    cohere_api_key: Optional[str] = None
    
    # File Upload
    max_upload_size_mb: int = 100
    upload_dir: str = "./uploads"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            # Fix for SQLAlchemy 2.0 compatibility
            return v.replace("postgres://", "postgresql://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
