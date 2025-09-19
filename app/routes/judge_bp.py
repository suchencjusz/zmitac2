import random
import string

from crud.player import get_player_by_nick
from decorators import judge_required
from extensions import db
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect
from models.models import Player
from werkzeug.security import generate_password_hash

csrf = CSRFProtect()


judge_bp = Blueprint("judge", __name__)


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


@judge_bp.route("/new_player", methods=["GET", "POST"])
@login_required
@judge_required
def new_player():
    if request.method == "POST":
        nick = request.form.get("nick")

        if not nick:
            flash("Proszę wypełnić pole nick!", "error")
            return render_template("judge/new_player.html")

        player = get_player_by_nick(db.session, nick)
        if player:
            flash("Gracz o takim nicku już istnieje!", "error")
            return render_template("judge/new_player.html")

        password = generate_random_password(12)

        player = Player(
            nick=nick,
            password=generate_password_hash(password),
            admin=False,
            judge=False,
        )
        db.session.add(player)
        db.session.commit()
        flash("Gracz dodany pomyślnie! Hasło: " + password, "success")
        return redirect(url_for("judge.new_player"))

    return render_template("judge/new_player.html")
