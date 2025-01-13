import os
from datetime import timedelta

from dotenv import load_dotenv
from pytz import timezone

load_dotenv()


class Config:
    SECRET_KEY = os.urandom(24)
    MONGO_URI = os.getenv("MONGO_URI")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "dupa1234")
    TIMEZONE = timezone("Europe/Warsaw")
    PERMANENT_SESSION_LIFETIME = timedelta(hours=6)
    DEBUG = os.getenv("DEBUG", False)
