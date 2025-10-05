from models.models import Match
from schemas.schemas import MatchCreate


def create_match(db, match: MatchCreate): # po co to jest
    db_match = Match(
        date=match.date,
        is_ranked=match.is_ranked,
        additional_info=match.additional_info,
        game_mode_id=match.game_mode_id,
        creator_id=match.creator_id,
    )

    db.add(db_match)
    db.flush()
    # db.flush -> zwraca id bez commita
    # ! logika zarzadza commitem !

    return db_match


def get_match_by_id(db, match_id: int):
    return db.query(Match).filter(Match.id == match_id).first()


def get_all_matches(db):
    return db.query(Match).all()
