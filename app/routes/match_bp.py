import datetime

from crud.match_player import get_all_matches_with_nicknames
from crud.player import get_all_players
from decorators import judge_required
from extensions import get_db
from flask import Blueprint, flash, render_template, request, redirect
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFProtect
from schemas.schemas import MatchCreateWithPlayersID
from services.match_service import MatchService

csrf = CSRFProtect()


match_bp = Blueprint("match", __name__)


@match_bp.route("/all", methods=["GET"])
def all():
    matches = get_all_matches_with_nicknames(get_db())
    return render_template("match/all.html", matches=matches)


# todo: game from db ofc
# @match_bp.route("/info", methods=["GET"])
# def game():
#     return render_template("match/info.html")

@match_bp.route("/info/<int:match_id>", methods=["GET"])
def info(match_id):
    match_players, match_record = MatchService.get_match_details_by_id(get_db(), match_id)

    if not match_record:
        flash("Mecz o podanym ID nie istnieje.", "danger")
        return redirect("/match/all")
    # to do:
    # tu skonczyles i
    # https://127.0.0.1:5001/match/info/1 nie dziala

    print(match_players)
    print(match_record)

    return render_template(
        "match/info.html",
        match=match_record,
        match_players=match_players,
    )
    


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
        match_data = MatchCreateWithPlayersID(
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
