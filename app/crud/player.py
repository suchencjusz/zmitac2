from models.models import Player
from schemas.schemas import PlayerCreate
from sqlalchemy.orm import Session


def get_player(db: Session, player_id: int) -> Player:
    return db.query(Player).filter(Player.id == player_id).first()

def get_player_by_nick(db: Session, nick: str) -> Player:
    return db.query(Player).filter(Player.nick == nick).first()

def get_players(db: Session) -> list[Player]:
    return db.query(Player).all()


def create_player(db: Session, player: PlayerCreate) -> Player:
    db_player = Player(
        nick=player.nick,
        password=player.password,
        keys=player.keys,
        judge=player.judge,
        admin=player.admin,
        elo=player.elo,
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def delete_player(db: Session, player_id: int) -> Player:
    db_player = get_player(db, player_id)
    if db_player:
        db.delete(db_player)
        db.commit()
    return db_player
