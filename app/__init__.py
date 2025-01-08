from flask import Flask
from pymongo import MongoClient

from config import Config

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)

client = MongoClient(app.config["MONGO_URI"])
db = client.get_default_database()

from app import routes
