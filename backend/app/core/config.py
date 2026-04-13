"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "k8s-inspector"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v2"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/k8s_inspector"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Kubernetes
    KUBECONFIG_PATH: Optional[str] = None  # Uses default ~/.kube/config if None
    CLUSTER_POLL_INTERVAL_SECONDS: int = 30
    MAX_CONCURRENT_CLUSTER_SCANS: int = 5
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # ML/Analytics
    ANOMALY_DETECTION_ENABLED: bool = True
    PREDICTION_HORIZON_HOURS: int = 24
    BASELINE_DAYS: int = 7
    
    # Cost
    CLOUD_PRICING_API_ENABLED: bool = True
    DEFAULT_CURRENCY: str = "USD"
    
    # Alerts
    ALERT_COOLDOWN_MINUTES: int = 15
    MAX_ALERTS_PER_HOUR: int = 50
    
    # Integrations
    SLACK_WEBHOOK_URL: Optional[str] = None
    TEAMS_WEBHOOK_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
