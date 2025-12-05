"""
Application configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "YiriAi"
    app_version: str = "2.0.0"
    debug: bool = False
    port: int = 8000
    host: str = "0.0.0.0"
    
    # GSU PAWS Configuration
    gsu_paws_base_url: str = "https://www.gosolar.gsu.edu"
    gsu_paws_schedule_url: str = "https://www.gosolar.gsu.edu/bprod/bwckschd.p_disp_dyn_sched"
    gsu_school_code: str = "GSU"
    
    # RateMyProfessors Configuration
    rmp_base_url: str = "https://www.ratemyprofessors.com"
    rmp_graphql_url: str = "https://www.ratemyprofessors.com/graphql"
    rmp_school_id: str = "U2Nob29sLTM1MQ=="  # GSU's base64 encoded ID
    rmp_authorization: str = "Basic dGVzdDp0ZXN0"
    
    # Database Configuration
    database_url: str = "postgresql+asyncpg://yiriai:yiriai_pass@localhost:5432/yiriai_db"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    redis_max_connections: int = 50
    
    # Cache TTL (in seconds)
    cache_ttl_courses: int = 3600  # 1 hour for course data
    cache_ttl_professor: int = 86400  # 24 hours for professor ratings
    cache_ttl_schedule: int = 1800  # 30 minutes for schedule searches
    
    # Scraping Configuration
    scraper_timeout: int = 30
    scraper_max_retries: int = 3
    scraper_retry_delay: int = 2
    scraper_concurrent_requests: int = 5
    scraper_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_calls: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # CORS
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]


# Global settings instance
settings = Settings()
