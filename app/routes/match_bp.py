from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect

from extensions import get_db

from crud.player import get_players

from decorators import judge_required

csrf = CSRFProtect()


match_bp = Blueprint("match", __name__)


@match_bp.route("/info", methods=["GET"])
def info():
    return render_template("match/info.html")


# todo: game from db ofc
@match_bp.route("/game", methods=["GET"])
def game():
    return render_template("match/game.html")


@match_bp.route("/add", methods=["GET", "POST"])
@login_required
@judge_required
def add():

    if request.method == "POST":
        pass

    players = get_players(get_db())

    return render_template(
        "match/add.html",
        players=players,
        is_admin=current_user.admin,
    )
