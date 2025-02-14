import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

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

    class Config:
        orm_mode = True

#
# --- PLAYER ---
#

class PlayerBase(BaseModel):
    nick: str
    judge: bool = False
    admin: bool = False
    elo: float = 1000.0
    keys: Optional[List[Dict[str, Any]]] = []

class PlayerCreate(PlayerBase):
    password: str

class PlayerOut(PlayerBase):
    id: int

    class Config:
        orm_mode = True

#
# --- MATCH ---
#

class MatchBase(BaseModel):
    date: datetime.datetime = datetime.timezone.utc
    is_ranked: bool = True
    additional_info: Optional[str] = None
    game_mode_id: int  

class MatchCreate(MatchBase):
    pass

class MatchOut(MatchBase):
    id: int
    game_mode: GameModeOut

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True
