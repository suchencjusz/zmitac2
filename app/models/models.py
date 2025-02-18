import datetime

from extensions import db
from flask_login import UserMixin


class GameMode(db.Model):
    __tablename__ = "game_modes"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, unique=True, nullable=False)  # e.g. "8-ball", "9-ball"
    description = db.Column(db.String, nullable=True)

    matches = db.relationship("Match", back_populates="game_mode")


# class Player(UserMixin, db.Model):
#     __tablename__ = "players"

#     id = db.Column(db.Integer, primary_key=True, index=True)
#     nick = db.Column(db.String, unique=True, index=True, nullable=False)
#     password = db.Column(db.String, nullable=False)
#     keys = db.Column(db.JSON, nullable=True)  # For webauthn/fido2 keys
#     judge = db.Column(db.Boolean, default=False)
#     admin = db.Column(db.Boolean, default=False)
#     elo = db.Column(db.Float, default=1000.0)

#     matches = db.relationship("MatchPlayer", back_populates="player")


# todo:
class Player(UserMixin, db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nick = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    judge = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    elo = db.Column(db.Float, default=1000.0)
    
    current_challenge = db.Column(db.String(128), nullable=True)  # Store registration/authentication challenges
    webauthn_user_id = db.Column(db.String(64), unique=True, nullable=True)  # Unique WebAuthn user identifier

    matches = db.relationship("MatchPlayer", back_populates="player")
    webauthn_credentials = db.relationship(
        "WebauthnCredential",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    def get_webauthn_credential(self, credential_id: str) -> "WebauthnCredential":
        return next(
            (cred for cred in self.webauthn_credentials if cred.credential_id == credential_id),
            None
        )

class WebauthnCredential(db.Model):
    __tablename__ = "webauthn_credentials"

    id = db.Column(db.Integer, primary_key=True, index=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    
    credential_id = db.Column(db.String(250), unique=True, nullable=False)
    public_key = db.Column(db.LargeBinary, nullable=False)
    sign_count = db.Column(db.Integer, nullable=False, default=0)
    
    aaguid = db.Column(db.String(36), nullable=True)  # 36 chars for UUID
    attestation_type = db.Column(db.String(32), nullable=True)
    transport = db.Column(db.String(32), nullable=True)  # platform, cross-platform, etc.
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_used_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    name = db.Column(db.String(64), nullable=True)  # User-friendly device name
    is_active = db.Column(db.Boolean, default=True)  # Allow disabling credentials

    player = db.relationship("Player", back_populates="webauthn_credentials")

    def __repr__(self):
        return f"<WebauthnCredential id={self.id} name={self.name}>"

    def update_sign_count(self, new_count: int) -> None:
        """Update the signature counter and last used timestamp"""
        if new_count <= self.sign_count:
            raise ValueError("New sign count must be greater than current count")
        self.sign_count = new_count
        self.last_used_at = datetime.datetime.now(datetime.timezone.utc)


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
