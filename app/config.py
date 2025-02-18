from dotenv import load_dotenv

load_dotenv()

from datetime import timedelta

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytz import timezone


class Config(BaseSettings):
    SECRET_KEY: SecretStr = Field(None, description="Secret key for sessions")
    DATABASE_URL: str = Field("", description="Database connection string")
    ADMIN_PASSWORD: SecretStr = Field(None, description="Admin password")
    TIMEZONE: str = Field(default="Europe/Warsaw", description="Application timezone")
    PERMANENT_SESSION_LIFETIME: int = Field(default=259200, description="Session lifetime in seconds")  # 3 days
    WTF_CSRF_ENABLED: bool = Field(True, description="CSRF protection flag")
    DEBUG: bool = Field(False, description="Debug mode flag")
    TESTING: bool = Field(False, description="Testing mode flag")

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


class TestConfig(Config):
    TESTING: bool = True
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:5432/zmitac_test"
    SECRET_KEY: SecretStr = Field(default="test_secret_key")
    WTF_CSRF_ENABLED: bool = False
    DEBUG: bool = False
    ADMIN_PASSWORD: SecretStr = Field(default="admin123")

    model_config = SettingsConfigDict(
        env_file=None,
        validate_assignment=True,
        extra="ignore",
    )
