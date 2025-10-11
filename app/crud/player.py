from crud import commit_or_flush
from models.models import Player
from schemas.schemas import PlayerCreate
from sqlalchemy.orm import Session


def get_player_by_id(db: Session, player_id: int) -> Player:
    return db.query(Player).filter(Player.id == player_id).first()


def get_player_by_nick(db: Session, nick: str) -> Player:
    return db.query(Player).filter(Player.nick == nick).first()


def get_all_players(db: Session) -> list[Player]:
    return db.query(Player).order_by(Player.nick).all()


def create_player(db: Session, player: PlayerCreate, commit=True) -> Player:
    db_player = Player(
        nick=player.nick,
        password=player.password,
        admin=player.admin,
        judge=player.judge,
        elo=player.elo,
    )

    db.add(db_player)
    commit_or_flush(db, db_player, commit)
    return db_player


def update_player_elo(db: Session, player: Player, new_elo: float, commit=True) -> Player:
    if new_elo < 0:
        new_elo = 0.0

    player.elo = new_elo
    commit_or_flush(db, player, commit)
    return player


def delete_player(db: Session, player_id: int, commit=True) -> Player:
    db_player = get_player_by_id(db, player_id)
    if db_player:
        db.delete(db_player)
        commit_or_flush(db, None, commit)

    return db_player
