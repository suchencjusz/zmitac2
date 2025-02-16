from datetime import timedelta
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytz import timezone


class Config(BaseSettings):
    SECRET_KEY: SecretStr = Field(None, description="Secret key for sessions")
    DATABASE_URL: str = Field(
        "", description="Database connection string"
    )
    ADMIN_PASSWORD: SecretStr = Field(None, description="Admin password")
    TIMEZONE: str = Field(default="Europe/Warsaw", description="Application timezone")
    PERMANENT_SESSION_LIFETIME: int = Field(
        default=259200, description="Session lifetime in seconds"  # 3 days 
    )
    DEBUG: bool = Field(False, description="Debug mode flag")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        validate_assignment=True,
        extra="ignore",  # ignore extre env variables
    )

    def get_timezone(self):
        """Get timezone object from string."""
        return timezone(self.TIMEZONE)

    def get_session_lifetime(self):
        """Get timedelta object from seconds."""
        return timedelta(seconds=self.PERMANENT_SESSION_LIFETIME)
