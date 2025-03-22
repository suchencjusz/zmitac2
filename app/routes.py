import csv
import os
import tempfile
from datetime import datetime, timedelta

import os
import tempfile

from flask import flash, redirect, render_template, request, send_file, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pytz import timezone

from app import app
from app.queries import (
    add_match,
    add_player,
    check_player_exists,
    get_all_matches,
    get_all_player_matches_by_nickname,
    get_all_players,
    get_matches_from_today,
    get_most_active_player_today,
    get_most_winning_player_today,
    get_player_by_id,
    get_player_matches_data_by_nickname,
    get_players_with_best_win_ratio,
)
from config import Config

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["10000 per day", "1000 per hour"],
)


@app.route("/")
def index():
    matches_today = list(get_matches_from_today())
    winner_today = get_most_winning_player_today()
    most_active_today = get_most_active_player_today()

    return render_template(
        "index.html", matches_today=matches_today, winner_today=winner_today, most_active_today=most_active_today
    )


@app.route("/add_player", methods=["GET", "POST"])
def add_player_route():
    if not session.get("logged_in"):
        flash("Panocku zaloguj się!", "error")
        return redirect(url_for("login"))
    if request.method == "POST":
        try:
            nickname = request.form["nickname"]
            add_player(nickname)
            flash("Gracz został dodany :D !", "success")
            return redirect(url_for("add_player_route"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("add_player.html")


@app.route("/add_match", methods=["GET", "POST"])
def add_match_route():
    if not session.get("logged_in"):
        flash("Panocku zaloguj się!", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            game_type = request.form["game_type"]
            who_won = request.form["who_won"]
            date_val = request.form["date"]
            time_val = request.form["time"]

            match_datetime = datetime.strptime(f"{date_val} {time_val}", "%Y-%m-%d %H:%M")

            if game_type == "multi":
                players1 = request.form.getlist("players1[]")
                players2 = request.form.getlist("players2[]")

                if not players1 or not players2:
                    flash("Panocku wybierz tych graczy!", "error")
                    return redirect(url_for("add_match_route"))

                add_match(
                    who_won=who_won,
                    date=match_datetime,
                    multi_game=True,
                    players1=players1,
                    players2=players2,
                )
            else:
                player1id = request.form["player1id"]
                player2id = request.form["player2id"]

                add_match(
                    player1id=player1id,
                    player2id=player2id,
                    who_won=who_won,
                    date=match_datetime,
                )

            flash("Mecz dodany sukcesywnie!!!!", "success")
            return redirect(url_for("add_match_route"))

        except Exception as e:
            flash(str(e), "error")

    now = datetime.now(app.config["TIMEZONE"])
    return render_template(
        "add_match.html",
        players=list(get_all_players()),
        today=now.date().isoformat(),
        now=now.strftime("%H:%M"),
    )


@app.route("/player/<nickname>")
def player(nickname):
    if not check_player_exists(nickname):
        flash("Nie znaleziono gracza!", "error")
        return redirect(url_for("index"))

    stats = get_player_matches_data_by_nickname(nickname)
    matches = list(get_all_player_matches_by_nickname(nickname))

    return render_template("player.html", player=player, stats=stats, matches=list(matches))


@app.route("/matches")
def matches():
    matches = list(get_all_matches())
    return render_template("matches.html", matches=matches)


@app.route("/info")
def info():
    return render_template("info.html")


@app.route("/players")
def players():
    players = list(get_all_players())
    return render_template("players.html", players=players)


@app.route("/ranking")
def ranking():
    best_ratio_players = get_players_with_best_win_ratio()

    return render_template("ranking.html", players=best_ratio_players)


@app.route("/export", methods=["GET"])
def export():
    if not session.get("logged_in"):
        flash("Panocku zaloguj się!", "error")
        return redirect(url_for("login"))

    all_matches = list(get_all_matches())

    temp_dir = tempfile.gettempdir()
    csv_path = os.path.join(temp_dir, "matches.csv")

    with open(csv_path, mode="w") as file:
        writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["id", "a", "b", "winner", "date", "multi_game"])

        for m in all_matches:
            a = []
            b = []

            if m["multi_game"]:
                for i in range(len(m["players1"])):
                    player1 = get_player_by_id(m["players1"][i])
                    player2 = get_player_by_id(m["players2"][i])
                    a.append(player1["nickname"])
                    b.append(player2["nickname"])
            else:
                a.append(get_player_by_id(m["player1id"])["nickname"])
                b.append(get_player_by_id(m["player2id"])["nickname"])

            writer.writerow([m["_id"], a, b, "a" if m["who_won"] == ("player1" or "players1") else "b", m["date"], m["multi_game"]])

    return send_file(csv_path, as_attachment=True, download_name="matches.csv")


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("8 per minute")
def login():
    if request.method == "POST":
        if request.form["password"] == Config.ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        flash("złe masło!!!", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
