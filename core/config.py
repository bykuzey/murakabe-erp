"""
MinimalERP - Configuration Module

Application settings and configuration management.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Murakabe AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = Field(..., min_length=32)

    # API
    API_V1_PREFIX: str = "/api/v1"
    API_TITLE: str = "Murakabe AI API"
    API_DOCS_URL: str = "/docs"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Redis
    REDIS_URL: str = Field(..., description="Redis connection string")

    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4000

    # GİB (Turkish Tax Administration)
    GIB_USERNAME: Optional[str] = None
    GIB_PASSWORD: Optional[str] = None
    GIB_ENV: str = "test"  # test or production
    GIB_WSDL_URL: str = "https://efaturatest.gib.gov.tr/"
    GIB_TIMEOUT: int = 30

    # e-Arşiv
    EARSIV_USERNAME: Optional[str] = None
    EARSIV_PASSWORD: Optional[str] = None

    # Bank Integrations
    BANK_API_ENABLED: bool = False

    # PayTR (Turkish Payment Gateway)
    PAYTR_MERCHANT_ID: Optional[str] = None
    PAYTR_MERCHANT_KEY: Optional[str] = None
    PAYTR_MERCHANT_SALT: Optional[str] = None

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@minimalerp.com.tr"
    SMTP_TLS: bool = True

    # SMS
    SMS_PROVIDER: str = "netgsm"
    SMS_API_KEY: Optional[str] = None
    SMS_USERNAME: Optional[str] = None
    SMS_PASSWORD: Optional[str] = None

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "jpg", "jpeg", "png", "xlsx", "xls", "docx"]
    UPLOAD_FOLDER: str = "/app/uploads"

    # AI Models
    AI_MODELS_PATH: str = "/app/ai_models"
    ENABLE_OCR: bool = True
    ENABLE_FORECASTING: bool = True
    ENABLE_ANOMALY_DETECTION: bool = True

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "Europe/Istanbul"
    CELERY_ENABLE_UTC: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/minimalerp.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    HTTPS_ONLY: bool = False
    SESSION_COOKIE_SECURE: bool = False
    CSRF_COOKIE_SECURE: bool = False

    # KVKK (Turkish GDPR)
    DATA_RETENTION_DAYS: int = 3650  # 10 years
    ENABLE_DATA_ENCRYPTION: bool = True
    ENABLE_AUDIT_LOG: bool = True

    # Turkish Localization
    TIMEZONE: str = "Europe/Istanbul"
    LANGUAGE: str = "tr"
    CURRENCY: str = "TRY"
    DATE_FORMAT: str = "%d.%m.%Y"
    TIME_FORMAT: str = "%H:%M:%S"

    # Feature Flags
    FEATURE_AI_CASHFLOW_PREDICTION: bool = True
    FEATURE_AI_SALES_FORECAST: bool = True
    FEATURE_AI_DEMAND_FORECAST: bool = True
    FEATURE_AI_LEAD_SCORING: bool = True
    FEATURE_AI_ANOMALY_DETECTION: bool = True
    FEATURE_AI_DOCUMENT_OCR: bool = True

    # Cache
    CACHE_DEFAULT_TIMEOUT: int = 300
    CACHE_USER_SESSION_TIMEOUT: int = 3600

    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_PATH: str = "/app/backups"

    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090

    # Development
    AUTO_RELOAD: bool = True
    SHOW_SQL_QUERIES: bool = False

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v):
        """Parse allowed extensions from string or list"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
