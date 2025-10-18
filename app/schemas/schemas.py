import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

#
# --- GAME MODE ---
#


class GameModeBase(BaseModel):
    name: str
    description: Optional[str] = None


class GameModeCreate(GameModeBase):
    pass


class GameModeOut(GameModeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


#
# --- PLAYER ---
#


class PlayerBase(BaseModel):
    nick: str
    password: str
    judge: bool = False
    admin: bool = False
    elo: float = 1000.0


class PlayerCreate(PlayerBase):
    password: str


class PlayerOut(PlayerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PlayerLogin(BaseModel):
    nick: str
    password: str


#
# --- WEBAUTHN CREDENTIAL ---
#


# class WebAuthnCredentialBase(BaseModel):
#     player_id: int
#     credential_id: bytes
#     credential_public_key: bytes
#     current_sign_count: int = 0


# class WebAuthnCredentialCreate(WebAuthnCredentialBase):
#     date_created: datetime.datetime = datetime.datetime.now()

#     pass


# class WebAuthnCredentialOut(WebAuthnCredentialBase):
#     id: int

#     date_created: datetime.datetime
#     date_last_used: datetime.datetime

#     model_config = ConfigDict(from_attributes=True)


#
# --- MATCH ---
#


class MatchBase(BaseModel):
    date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    is_ranked: bool = True
    additional_info: Optional[str] = None
    game_mode_id: int

class MatchCreate(MatchBase):
    creator_id: int


class MatchCreateWithPlayersID(MatchCreate):
    players_ids_winners: list[int]
    players_ids_losers: list[int]


class MatchOut(MatchBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


#
# --- MATCH_PLAYER ---
#


class MatchPlayerBase(BaseModel):
    match_id: int
    player_id: int
    is_winner: bool
    elo_change: float

class MatchPlayerCreate(MatchPlayerBase):
    pass


class MatchPlayerOut(MatchPlayerBase):
    id: int
    player: PlayerOut
    match: MatchOut | None = None

    model_config = ConfigDict(from_attributes=True)

class MatchWithPlayers(MatchOut):
    winners: list[PlayerOut] = []
    losers: list[PlayerOut] = []
