from flask import Blueprint, render_template
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


match_bp = Blueprint("match", __name__)

@match_bp.route("/info", methods=["GET"])
def info():
    return render_template("match/info.html")

# todo: game from db ofc
@match_bp.route("/game", methods=["GET"])
def game():
    return render_template("match/game.html")
