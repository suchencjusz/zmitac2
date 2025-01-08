import os

from dotenv import load_dotenv

load_dotenv()  

class Config:
    SECRET_KEY = os.urandom(24)
    MONGO_URI = os.getenv("MONGO_URI")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "dupa1234")