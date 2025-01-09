from datetime import datetime

from flask import flash, redirect, render_template, request, session, url_for

from app import app
from app.queries import add_match, add_player, get_all_matches, get_all_players
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

            if game_type == "multi":
                players1 = request.form.getlist("players1[]")
                players2 = request.form.getlist("players2[]")

                if not players1 or not players2:
                    flash("Panocku wybierz tych graczy!", "error")
                    return redirect(url_for("add_match_route"))

                if set(players1) & set(players2):
                    flash(
                        "Panocku nie oszukuj jeden gracz jedna druzyna! Nie oszukuj!",
                        "error",
                    )
                    return redirect(url_for("add_match_route"))

                add_match(
                    player1id=None,
                    player2id=None,
                    who_won=who_won,
                    date=date_val,
                    time=time_val,
                    multi_game=True,
                    players1=players1,
                    players2=players2
                )
            else:
                player1id = request.form["player1id"]
                player2id = request.form["player2id"]
                add_match(
                    player1id=player1id,
                    player2id=player2id,
                    who_won=who_won,
                    date=date_val,
                    time=time_val
                )

            flash("Mecz dodany sukcesywnie!!!!", "success")
            return redirect(url_for("add_match_route"))
        except Exception as e:
            flash(str(e), "error")
            
    now = datetime.now()
    return render_template(
        "add_match.html", 
        players=list(get_all_players()), 
        today=now.date().isoformat(),
        now=now.strftime("%H:%M")
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == Config.ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        flash("złe masło!!!!!!!!!!!!!!!!!", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
