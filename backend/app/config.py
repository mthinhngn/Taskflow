from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Database
    database_url: str = "postgresql://user:password@db:5432/taskflow"
    
    # CORS - with default fallback
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"]
    )
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from JSON string or return default"""
        if isinstance(v, str):
            # Handle empty string
            if not v or v.strip() == "":
                return ["http://localhost:3000", "http://localhost:5173"]
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                # If parsing fails, return default
                return ["http://localhost:3000", "http://localhost:5173"]
        elif isinstance(v, list):
            return v
        # Fallback to default
        return ["http://localhost:3000", "http://localhost:5173"]


_settings = None


def get_settings() -> Settings:
    """Get cached settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings