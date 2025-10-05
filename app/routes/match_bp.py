from crud.player import get_all_players
from decorators import judge_required
from extensions import get_db
from flask import Blueprint, render_template, request, flash
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFProtect

import datetime

from services.match_service import MatchService
from schemas.schemas import MatchCreate

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

    def _create_match(
        date: datetime.datetime,
        is_ranked: bool,
        additional_info: str,
        game_mode_id: int,
        creator_id: int,
        players_ids_winners: list[int],
        players_ids_losers: list[int],
    ):
        match_data = MatchCreate(
            date=date,
            is_ranked=is_ranked,
            additional_info=additional_info,
            game_mode_id=game_mode_id,
            creator_id=creator_id,
            winner_ids=players_ids_winners,
            loser_ids=players_ids_losers,
        )

        try:
            MatchService.process_match(get_db(), match_data)
            flash("Mecz dodany pomyślnie.", "success")
        except Exception as e:
            print("Error processing match:", e)  # Debug print
            flash(f"Wystąpił błąd podczas dodawania meczu: {str(e)}", "danger")

    if request.method == "POST":
        form = request.form

        print("DEBUG: form data received:", form)  # Debug print

        teams = form.get("teams")
        ranked = form.get("ranked")
        players1 = form.getlist("players1")
        players2 = form.getlist("players2")
        winner = form.get("winner")
        date = form.get("date")
        time = form.get("time")

        teams = bool(teams)
        ranked = bool(ranked)

        if not players1 or not players2:
            flash("Musisz wybrać graczy.", "danger")
        elif set(players1) & set(players2):
            flash("Gracze nie mogą się powtarzać.", "danger")
        elif not winner:
            flash("Musisz wybrać zwycięzcę.", "danger")
        elif current_user.admin and (not date or not time):
            flash("Musisz podać datę i godzinę.", "danger")
        else:
            losers = players2 if players1 == winner else players1

            _create_match(
                date=datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M"),
                is_ranked=ranked,
                additional_info=form.get("additional_info"),
                game_mode_id=1,                 # narazie tylko basic 8
                creator_id=current_user.id,     # sprawdz czy id jest ok w sensie czy flask ogarnia to id z bazy
                players_ids_winners=winner,     # pydantic sie tu prul todo: !!
                players_ids_losers=losers,
            ) # wsm to nw czy to dziala xd todo:

    players = get_all_players(get_db())

    return render_template(
        "match/add.html",
        players=players,
        is_admin=current_user.admin,
    )
