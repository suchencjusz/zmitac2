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
            players_ids_winners=players_ids_winners,
            players_ids_losers=players_ids_losers,
        )

        try:
            MatchService.process_match(get_db(), match_data)
            flash("Mecz dodany pomyślnie.", "success")
        except Exception as e:
            flash(f"Wystąpił błąd podczas dodawania meczu: {str(e)}", "danger")

    if request.method == "POST":
        form = request.form

        teams = form.get("teams")
        ranked = form.get("ranked")
        players1 = form.getlist("players1")
        players2 = form.getlist("players2")
        winner = form.get("winner")
        additional_info = form.get("additional_info", "").strip()

        _date = form.get("date")
        _time = form.get("time")

        if not current_user.admin:
            date = datetime.datetime.now()
        else:
            date = datetime.datetime.strptime(f"{_date} {_time}", "%Y-%m-%d %H:%M")

        teams = bool(teams)
        is_ranked = bool(ranked)
        additional_info = additional_info if additional_info else None

        if not players1 or not players2:
            flash("Musisz wybrać graczy.", "danger")
        elif set(players1) & set(players2):
            flash("Gracze nie mogą się powtarzać.", "danger")
        elif not winner:
            flash("Musisz wybrać zwycięzcę.", "danger")
        elif len(players1) != len(players2):
            flash("Drużyny muszą mieć taki sam rozmiar.", "danger")
        else:
            _winners = []
            _losers = []

            if teams:
                if winner == "A":
                    _winners = [int(w) for w in players1]
                    _losers = [int(l) for l in players2]
                else:
                    _winners = [int(w) for w in players2]
                    _losers = [int(l) for l in players1]
            else:
                winner_id = int(winner)
                
                if winner in players1:
                    _winners = [winner_id]
                    _losers = [int(players2[0])]
                else:
                    _winners = [winner_id]
                    _losers = [int(players1[0])]

            _create_match(
                date=date,
                is_ranked=is_ranked,
                additional_info=additional_info,
                game_mode_id=1,
                creator_id=current_user.id,
                players_ids_winners=_winners,
                players_ids_losers=_losers,
            )

    players = get_all_players(get_db())

    return render_template(
        "match/add.html",
        players=players,
        is_admin=current_user.admin,
    )
