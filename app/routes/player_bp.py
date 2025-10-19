from crud.player import get_player_by_nick, get_all_players
from extensions import db
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


player_bp = Blueprint("player", __name__)

@player_bp.route("/all", methods=["GET"])
def all():
    players = get_all_players(db.session) # to do: zaokraglic to trzeba i sortowac po elo i wywalic w indeksie link
    return render_template("player/all.html", players=players)


@player_bp.route("/info/<string:player_nick>", methods=["GET"])
def info(player_nick):
    player = get_player_by_nick(db.session, player_nick)

    if player is None:
        flash("Nie znaleziono gracza o podanym nicku", "error")
        return redirect(url_for("index"))

    return render_template("player/info.html", player=player)
