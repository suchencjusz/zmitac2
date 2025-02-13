from datetime import timedelta
from typing import Optional

from pydantic import BaseSettings, Field
from pytz import timezone


class Config(BaseSettings):
    SECRET_KEY: str = Field("123", description="Secret key for Flask sessions")  # todo: dev only
    MONGO_URI: str = Field(..., description="MongoDB connection string")
    ADMIN_PASSWORD: str = Field("dupa1234", description="Admin password")
    TIMEZONE: timezone = Field(default_factory=lambda: timezone("Europe/Warsaw"))
    PERMANENT_SESSION_LIFETIME: timedelta = Field(default_factory=lambda: timedelta(days=3))
    DEBUG: bool = Field(False, description="Debug mode flag")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Config()
