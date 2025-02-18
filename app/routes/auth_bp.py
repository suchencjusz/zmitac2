from urllib.parse import urlparse

from crud.player import get_player_by_nick
from extensions import db
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from models.models import Player
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nick = request.form.get("nick")
        password = request.form.get("password")

        if not nick or not password:
            flash("Proszę wypełnić wszystkie pola!", "error")
            return render_template("auth/login.html")

        player = get_player_by_nick(db.session, nick)
        if player and check_password_hash(player.password, password):
            login_user(player)
            flash("Zalogowano pomyślnie!", "success")
            next_page = request.args.get("next", "")
            if next_page:
                next_page = next_page.replace("\\", "")
                if not urlparse(next_page).netloc and not urlparse(next_page).scheme:
                    return redirect(next_page)
            return redirect(url_for("index"))

        flash("Nieprawidłowy nick lub hasło!", "error")

    return render_template("auth/login.html")


# @auth_bp.route('/edit', methods=['GET', 'POST'])
# @login_required
# def edit():


@auth_bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        new_password2 = request.form.get("new_password2")

        if not old_password or not new_password or not new_password2:
            flash("Proszę wypełnić wszystkie pola!", "error")
            return render_template("auth/change_password.html")

        if not check_password_hash(current_user.password, old_password):
            flash("Nieprawidłowe stare hasło!", "error")
            return render_template("auth/change_password.html")

        if new_password != new_password2:
            flash("Nowe hasła nie są takie same!", "error")
            return render_template("auth/change_password.html")

        if len(new_password) < 10:
            flash("Nowe hasło musi mieć co najmniej 10 znaków!", "error")
            return render_template("auth/change_password.html")

        current_user.password = generate_password_hash(new_password)

        db.session.commit()
        flash("Hasło zostało zmienione!", "success")
        return redirect(url_for("index"))

    return render_template("auth/change_password.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Zostałeś wylogowany.", "info")
    return redirect(url_for("index"))
