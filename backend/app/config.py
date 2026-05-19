"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # DeepSeek
    DEEPSEEK_API_KEY: str
    DEEPSEEK_API_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Redis (optional)
    REDIS_URL: str = ""

    # App
    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # Development: allow all localhost ports
        if self.APP_ENV == "development":
            origins.append("http://localhost:5173")
            origins.append("http://localhost:5174")
            origins.append("http://localhost:5175")
            origins.append("http://localhost:5176")
            origins.append("http://localhost:3000")
        return origins

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
