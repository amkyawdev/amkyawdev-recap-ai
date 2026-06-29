"""
Application configuration
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Recap AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = None
    
    # S3/R2 Storage
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "recap-ai"
    S3_REGION: str = "us-east-1"
    
    # GPU Settings
    GPU_ENABLED: bool = True
    GPU_DEVICE_ID: int = 0
    GPU_MEMORY_FRACTION: float = 0.8
    MAX_GPU_JOBS: int = 2
    
    # Redis (Task Queue)
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Whisper
    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "cuda"
    
    # Video Processing
    MAX_VIDEO_SIZE_MB: int = 500
    SUPPORTED_VIDEO_FORMATS: list = ["mp4", "mov", "avi", "mkv", "webm"]
    MAX_VIDEO_DURATION_SECONDS: int = 3600  # 1 hour
    
    # Render Settings
    DEFAULT_VIDEO_CODEC: str = "h264_nvenc"
    DEFAULT_AUDIO_CODEC: str = "aac"
    DEFAULT_VIDEO_BITRATE: str = "5M"
    DEFAULT_AUDIO_BITRATE: str = "192k"
    
    # Storage
    TEMP_DIR: str = "/tmp/recap-ai"
    UPLOAD_DIR: str = "./uploads"
    OUTPUT_DIR: str = "./outputs"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure directories exist
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
