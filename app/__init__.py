from flask import Flask, session
from pymongo import MongoClient

from config import Config

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)

client = MongoClient(app.config["MONGO_URI"])
db = client.get_default_database()


@app.before_request
def make_session_permanent():
    session.permanent = True


from app import routes
