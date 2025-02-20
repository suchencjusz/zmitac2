from crud.player import get_player_by_nick, get_players
from decorators import admin_required
from extensions import db
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFProtect
from models.models import Player
from werkzeug.security import check_password_hash, generate_password_hash

csrf = CSRFProtect()

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/change_someone_password", methods=["GET", "POST"])
@login_required
@admin_required
def change_someone_password():
    if request.method == "POST":
        player_id = request.form.get("player_id")
        new_password = request.form.get("new_password")

        if not player_id or not new_password:
            flash("Proszę wypełnić wszystkie pola!", "error")
            return render_template("admin/change_someone_password.html")

        player = Player.query.get(player_id)

        if not player:
            flash("Gracz nie istnieje!", "error")
            return render_template("admin/change_someone_password.html")

        if player.admin:
            flash("Nie możesz zmienić hasła administratora!", "error")
            return render_template("admin/change_someone_password.html")

        player.password = generate_password_hash(new_password)
        db.session.commit()
        flash("Hasło zmienione pomyślnie!", "success")
        return redirect(url_for("admin.change_someone_password"))

    players = get_players(db.session)
    return render_template("admin/change_someone_password.html", players=players)


@admin_bp.route("/change_someone_permissions", methods=["GET", "POST"])
@login_required
@admin_required
def change_someone_permissions():
    if request.method == "POST":
        player_id = request.form.get("player_id")
        admin_perm = request.form.get("admin") == "true"
        judge_perm = request.form.get("judge") == "true"

        if not player_id:
            flash("Proszę wybrać gracza!", "error")
            return redirect(url_for("admin.change_someone_permissions"))

        player = Player.query.get(player_id)
        if not player:
            flash("Gracz nie istnieje!", "error")
            return redirect(url_for("admin.change_someone_permissions"))

        player.admin = admin_perm
        player.judge = judge_perm
        db.session.commit()
        flash("Uprawnienia zaktualizowane pomyślnie!", "success")
        return redirect(url_for("admin.change_someone_permissions"))

    players = get_players(db.session)
    return render_template("admin/change_someone_permissions.html", players=players)


@admin_bp.route("/update_player_permissions", methods=["GET", "POST"])
@login_required
@admin_required
def update_player_permissions():
    if request.method == "GET":
        player_id = request.args.get("player_id")
        if not player_id:
            return "Wybierz gracza", 400
        player = Player.query.get_or_404(player_id)
        return render_template("admin/_permissions_fragment.html", player=player)

    player_id = request.form.get("player_id")
    player = Player.query.get_or_404(player_id)

    player.admin = request.form.get("admin") == "on"
    player.judge = request.form.get("judge") == "on"
    db.session.commit()

    flash("Uprawnienia zostały zaktualizowane", "success")
    return redirect(url_for("admin.change_someone_permissions"))
