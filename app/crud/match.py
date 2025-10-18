from crud import commit_or_flush
from models.models import Match, GameMode
from schemas.schemas import MatchCreate, MatchOut, GameModeOut


def create_match(db, match: MatchCreate, commit=True):
    db_match = Match(
        date=match.date,
        is_ranked=match.is_ranked,
        additional_info=match.additional_info,
        game_mode_id=match.game_mode_id,
        creator_id=match.creator_id,
    )

    db.add(db_match)
    commit_or_flush(db, db_match, commit)
    return db_match


def get_match_by_id(db, match_id: int) -> MatchOut | None:
    db_match = db.query(Match).filter(Match.id == match_id).first()

    if db_match:
        return MatchOut(
            id=db_match.id,
            date=db_match.date,
            is_ranked=db_match.is_ranked,
            additional_info=db_match.additional_info,
            game_mode_id=db_match.game_mode_id,
            creator_id=db_match.creator_id,
        )
    return None

def get_all_matches(db):
    return db.query(Match).all()
