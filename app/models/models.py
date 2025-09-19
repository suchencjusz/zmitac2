import datetime

from extensions import db
from flask_login import UserMixin


class GameMode(db.Model):
    __tablename__ = "game_modes"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, unique=True, nullable=False)  # e.g. "8-ball", "9-ball"
    description = db.Column(db.String, nullable=True)

    matches = db.relationship("Match", back_populates="game_mode")


class Player(UserMixin, db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nick = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    judge = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    elo = db.Column(db.Float, default=1000.0)
    info = db.Column(db.String, nullable=True)  # info odnosnie sie gracza dla adminow, rozszyfrowanie nicku np.

    matches = db.relationship("MatchPlayer", back_populates="player")
    webauthn_credentials = db.relationship("WebAuthnCredential", back_populates="player", cascade="all, delete-orphan")


class WebAuthnCredential(db.Model):
    __tablename__ = "webauthn_credentials"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    credential_id = db.Column(db.LargeBinary, nullable=False)
    credential_public_key = db.Column(db.LargeBinary, nullable=False)
    current_sign_count = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    date_last_used = db.Column(db.DateTime, default=datetime.datetime.now)

    player = db.relationship("Player", back_populates="webauthn_credentials")

    def __repr__(self):
        return f"<Credential {self.credential_id}>"


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True, index=True)
    creator_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
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
