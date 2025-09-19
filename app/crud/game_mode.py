from models.models import GameMode
from sqlalchemy.orm import Session


def get_game_mode_by_name(db: Session, name: str) -> GameMode:
    return db.query(GameMode).filter(GameMode.name == name).first()


def get_game_mode(db: Session, game_mode_id: int) -> GameMode:
    return db.query(GameMode).filter(GameMode.id == game_mode_id).first()


def get_game_modes(db: Session) -> list[GameMode]:
    return db.query(GameMode).order_by(GameMode.name).all()


def create_game_mode(db: Session, game_mode: GameMode) -> GameMode:
    db_game_mode = GameMode(
        name=game_mode.name,
        description=game_mode.description,
    )

    db.add(db_game_mode)
    db.commit()
    db.refresh(db_game_mode)
    return db_game_mode


def update_game_mode(db: Session, game_mode_id: int, game_mode: GameMode) -> GameMode:
    db_game_mode = get_game_mode(db, game_mode_id)
    if db_game_mode:
        db_game_mode.name = game_mode.name
        db_game_mode.description = game_mode.description
        db.commit()
    return db_game_mode
