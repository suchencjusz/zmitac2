from crud.player import get_player_by_nick, get_all_players
from crud.match import get_last_match
from extensions import db, generate_elegant_datetime_ago
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_wtf.csrf import CSRFProtect

from schemas.schemas import MatchOut

csrf = CSRFProtect()


index_bp = Blueprint("index", __name__)

@index_bp.route("/", methods=["GET"])
def index():

    last_match: MatchOut = get_last_match(db.session)
    last_match_str: str = ""
    
    if last_match:
        last_match_str = generate_elegant_datetime_ago(last_match.date)

    return render_template("index.html", last_match_str=last_match_str)