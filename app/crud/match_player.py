from models.models import MatchPlayer
from schemas.schemas import MatchPlayerCreate
from crud import commit_or_flush


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
