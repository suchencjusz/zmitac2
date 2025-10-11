from crud import commit_or_flush
from models.models import Match, MatchPlayer
from schemas.schemas import (
    MatchPlayerCreate,
    MatchPlayerOut,
    MatchWithPlayers,
    PlayerOut,
)
from sqlalchemy.orm import joinedload


def create_match_player(db, match_player: MatchPlayerCreate, commit=True):
    db_match_player = MatchPlayer(
        player_id=match_player.player_id,
        match_id=match_player.match_id,
        elo_change=match_player.elo_change,
        is_winner=match_player.is_winner,
    )

    db.add(db_match_player)
    commit_or_flush(db, db_match_player, commit)
    return db_match_player


def get_match_player(db, match_player_id: int) -> MatchPlayerOut | None:
    db_match_player = (
        db.query(MatchPlayer).filter(MatchPlayer.id == match_player_id).first()
    )
    if db_match_player:
        return MatchPlayerOut(
            id=db_match_player.id,
            player_id=db_match_player.player_id,
            match_id=db_match_player.match_id,
            elo_change=db_match_player.elo_change,
            is_winner=db_match_player.is_winner,
        )
    return None


def get_all_match_players(db) -> list[MatchPlayerOut]:
    db_match_players = db.query(MatchPlayer).all()
    return [
        MatchPlayerOut(
            id=mp.id,
            player_id=mp.player_id,
            match_id=mp.match_id,
            elo_change=mp.elo_change,
            is_winner=mp.is_winner,
        )
        for mp in db_match_players
    ]


def get_all_matches_with_nicknames(db) -> list[MatchWithPlayers]:

    # mankament nie spojosci nazw players->match_players (dupcyc to)

    matches = (
        db.query(Match)
        .options(
            joinedload(Match.players).joinedload(MatchPlayer.player),
            joinedload(Match.game_mode),
        )
        .order_by(Match.date.desc())
        .all()
    )

    result = []
    for match in matches:
        winners = [mp.player for mp in match.players if mp.is_winner]
        losers = [mp.player for mp in match.players if not mp.is_winner]

        match_data = MatchWithPlayers(
            id=match.id,
            date=match.date,
            is_ranked=match.is_ranked,
            additional_info=match.additional_info,
            game_mode_id=match.game_mode_id,
            game_mode=match.game_mode,
            winners=[PlayerOut.model_validate(w) for w in winners],
            losers=[PlayerOut.model_validate(l) for l in losers],
        )
        result.append(match_data)

    return result


# def get_all_matches_with_nicknames(db) -> list[MatchWithPlayers]:
#     matches = db.query(Match).order_by(Match.date.desc()).all()
#     result = []
#
#     for match in matches:
#         winners = db.query(Player).join(MatchPlayer).filter(
#             MatchPlayer.match_id == match.id,
#             MatchPlayer.is_winner == True
#         ).all()
#
#         losers = db.query(Player).join(MatchPlayer).filter(
#             MatchPlayer.match_id == match.id,
#             MatchPlayer.is_winner == False
#         ).all()
#
#         match_data = MatchWithPlayers(
#             id=match.id,
#             date=match.date,
#             is_ranked=match.is_ranked,
#             additional_info=match.additional_info,
#             game_mode_id=match.game_mode_id,
#             game_mode=match.game_mode,
#             winners=[PlayerOut.model_validate(w) for w in winners],
#             losers=[PlayerOut.model_validate(l) for l in losers]
#         )
#         result.append(match_data)
#
#     return result
