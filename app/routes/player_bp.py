from crud.player import get_player_by_nick
from extensions import db
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


player_bp = Blueprint("player_bp", __name__)


@player_bp.route("/info/<string:player_nick>", methods=["GET"])
def info(player_nick):
    player = get_player_by_nick(db.session, player_nick)

    if player is None:
        flash("Nie znaleziono gracza o podanym nicku", "error")
        return redirect(url_for("index"))

    return render_template("player/info.html", player=player)
