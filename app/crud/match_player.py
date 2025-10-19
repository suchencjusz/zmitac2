from crud import commit_or_flush
from models.models import Match, MatchPlayer, Player
from schemas.schemas import (
    MatchPlayerCreate,
    MatchPlayerOut,
    MatchWithPlayers,
    PlayerOut,
)

from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_, or_, select



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


# def get_match_player(db, match_player_id: int) -> MatchPlayerOut | None:
#     db_match_player = (
#         db.query(MatchPlayer).filter(MatchPlayer.id == match_player_id).first()
#     )
#     if db_match_player:
#         return MatchPlayerOut(
#             id=db_match_player.id,
#             player_id=db_match_player.player_id,
#             match_id=db_match_player.match_id,
#             elo_change=db_match_player.elo_change,
#             is_winner=db_match_player.is_winner,
#         )
#     return None


# def get_all_match_players(db) -> list[MatchPlayerOut]:
#     db_match_players = db.query(MatchPlayer).all()
#     return [
#         MatchPlayerOut(
#             id=mp.id,
#             player_id=mp.player_id,
#             match_id=mp.match_id,
#             elo_change=mp.elo_change,
#             is_winner=mp.is_winner,
#         )
#         for mp in db_match_players
#     ]

def get_match_players_by_match_id(db, match_id: int) -> list[MatchPlayerOut]:
    db_match_players = (
        db.query(MatchPlayer).filter(MatchPlayer.match_id == match_id).all()
    )
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

def get_match_players_elo_changes_by_match_id(db, match_id: int) -> list[MatchPlayerOut] | None:

    # z racji z jakiegos pwoodu nie zapisduje elo_beofre i elo_after, sumuje zmieione elo :D

    BASE_ELO = 1000.0

    match_ref = db.query(Match.id, Match.date).filter(Match.id == match_id).one_or_none()
    if not match_ref:
        return None
    target_date, target_id = match_ref.date, match_ref.id

    players_subq = (
        db.query(MatchPlayer.player_id)
        .filter(MatchPlayer.match_id == match_id)
        .subquery()
    )

    hist = (
        db.query(
            MatchPlayer.id.label("mp_id"),
            MatchPlayer.match_id.label("match_id"),
            MatchPlayer.player_id.label("player_id"),
            MatchPlayer.is_winner.label("is_winner"),
            MatchPlayer.elo_change.label("elo_change"),
            func.sum(MatchPlayer.elo_change)
            .over(
                partition_by=MatchPlayer.player_id,
                order_by=(Match.date, Match.id),
            )
            .label("cum_delta"),
        )
        .join(Match, Match.id == MatchPlayer.match_id)
        .filter(
            MatchPlayer.player_id.in_(select(players_subq.c.player_id)),
            or_(
                Match.date < target_date,
                and_(Match.date == target_date, Match.id <= target_id),
            ),
        )
        .subquery()
    )

    rows = (
        db.query(
            hist.c.match_id,
            hist.c.player_id,
            hist.c.is_winner,
            hist.c.elo_change,
            hist.c.cum_delta,
            MatchPlayer.id,
        )
        .join(MatchPlayer, MatchPlayer.id == hist.c.mp_id)
        .join(Player, Player.id == hist.c.player_id)
        .filter(hist.c.match_id == match_id)
        .add_columns(Player)
        .all()
    )

    results: list[MatchPlayerOut] = []
    for match_id_, player_id, is_winner, elo_change, cum_delta, mp_id, player in rows:
        elo_after = BASE_ELO + float(cum_delta or 0.0)
        player_out = PlayerOut.model_validate(player).model_copy(
            update={"elo": round(elo_after, 1)}
        )
        results.append(
            MatchPlayerOut(
                match_id=match_id_,
                player_id=player_id,
                is_winner=is_winner,
                elo_change=round(float(elo_change or 0.0), 1),
                player=player_out,
                id=mp_id,
            )
        )
    return results

# def get_match_players_elo_changes_by_match_id(db, match_id: int) -> list[MatchPlayerOut] | None:
#     db_match_players = (
#         db.query(MatchPlayer)
#         .options(joinedload(MatchPlayer.player))
#         .filter(MatchPlayer.match_id == match_id)
#         .all()
#     )
#
#     results: list[MatchPlayerOut] = []
#
#     for mp in db_match_players:
#         elo_change_rounded = round(mp.elo_change, 1)
#
#         player_out = PlayerOut.model_validate(mp.player) if mp.player else None
#         if player_out and getattr(player_out, "elo", None) is not None:
#             player_out = player_out.model_copy(update={"elo": round(player_out.elo, 1)})
#
#         results.append(
#             MatchPlayerOut(
#                 match_id=mp.match_id,
#                 player_id=mp.player_id,
#                 is_winner=mp.is_winner,
#                 elo_change=elo_change_rounded,
#                 player=player_out,
#                 id=mp.id,
#             )
#         )
#
#     return results


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
            creator_id=match.creator_id,
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
