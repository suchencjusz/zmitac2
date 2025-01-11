from datetime import datetime, timedelta

from flask import flash, redirect, render_template, request, session, url_for
from pytz import timezone

from app import app
from app.queries import (
    add_match,
    add_player,
    check_player_exists,
    get_all_matches,
    get_all_player_matches_by_nickname,
    get_all_players,
    get_player_matches_data_by_nickname,
)
from config import Config


@app.route("/")
def index():
    matches = list(get_all_matches())
    return render_template("index.html", matches=matches)


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

            match_datetime = datetime.strptime(
                f"{date_val} {time_val}", "%Y-%m-%d %H:%M"
            )

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

    return render_template(
        "player.html", player=player, stats=stats, matches=list(matches)
    )


@app.route("/matches")
def matches():
    matches = list(get_all_matches())
    return render_template("matches.html", matches=matches)


@app.route("/login", methods=["GET", "POST"])
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
