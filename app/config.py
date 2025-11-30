from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "postgresql+asyncpg://newsuser:newspassword@localhost:5432/thai_news"
    database_url_sync: str = "postgresql://newsuser:newspassword@localhost:5432/thai_news"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    api_workers: int = 4
    api_key: str = "change-this-secret-key"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Scraper
    scraper_user_agent: str = "ThaiNewsBot/1.0 (+https://yourwebsite.com/bot)"
    scraper_timeout: int = 30
    scraper_max_retries: int = 3
    scraper_delay_seconds: int = 2
    scraper_respect_robots_txt: bool = True
    
    # Scheduler
    scheduler_enabled: bool = True
    scheduler_fetch_interval_minutes: int = 30
    
    # Webhook Notifications (n8n)
    webhook_enabled: bool = False
    webhook_url: str = ""  # n8n webhook URL
    webhook_secret: str = ""  # Optional: for webhook authentication
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Sources
    sources_config_path: str = "sources.yaml"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
