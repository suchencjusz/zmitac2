import datetime
from flask_login import UserMixin
from extensions import db

class GameMode(db.Model):
    __tablename__ = "game_modes"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, unique=True, nullable=False)  # e.g. "8-ball", "9-ball"
    description = db.Column(db.String, nullable=True)

    matches = db.relationship("Match", back_populates="game_mode")


class Player(UserMixin, db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nick = db.Column(db.String, unique=True, index=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    keys = db.Column(db.JSON, nullable=True)  # For webauthn/fido2 keys
    judge = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    elo = db.Column(db.Float, default=1000.0)

    matches = db.relationship("MatchPlayer", back_populates="player")


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True, index=True)
    date = db.Column(db.DateTime, default=datetime.timezone.utc)
    is_ranked = db.Column(db.Boolean, default=True)
    additional_info = db.Column(db.String, nullable=True)
    game_mode_id = db.Column(db.Integer, db.ForeignKey("game_modes.id"), nullable=False)

    game_mode = db.relationship("GameMode", back_populates="matches")
    players = db.relationship("MatchPlayer", back_populates="match")


class MatchPlayer(db.Model):
    __tablename__ = "match_players"

    id = db.Column(db.Integer, primary_key=True, index=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    is_winner = db.Column(db.Boolean, nullable=False)
    elo_change = db.Column(db.Float, nullable=False)

    match = db.relationship("Match", back_populates="players")
    player = db.relationship("Player", back_populates="matches")