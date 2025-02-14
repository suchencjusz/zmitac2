import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class GameMode(Base):
    __tablename__ = "game_modes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # "8-ball", "9-ball"
    description = Column(String, nullable=True)  

    matches = relationship("Match", back_populates="game_mode")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    nick = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    keys = Column(JSONB, nullable=True)  # webauthn/fido2 keys
    judge = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    elo = Column(Float, default=1000.0)
    # wins = Column(Integer, default=0) redundancja
    # loses = Column(Integer, default=0)

    matches = relationship("MatchPlayer", back_populates="player")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.timezone.utc)
    is_ranked = Column(Boolean, default=True)
    additional_info = Column(String, nullable=True)    
    game_mode_id = Column(Integer, ForeignKey("game_modes.id"), nullable=False)

    game_mode = relationship("GameMode", back_populates="matches")
    players = relationship("MatchPlayer", back_populates="match")


class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    is_winner = Column(Boolean, nullable=False)
    elo_change = Column(Float, nullable=False)

    match = relationship("Match", back_populates="players")
    player = relationship("Player", back_populates="matches")
