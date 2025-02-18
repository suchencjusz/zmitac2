import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

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

#
# --- WEBAUTHN CREDENTIAL ---
#

# todo
# read about webauthn
# do login with it
# fix default admin account

class WebauthnCredentialBase(BaseModel):
    player_id: int
    credential_id: str
    public_key: bytes
    sign_count: int = 0
    aaguid: Optional[str] = None  # authenticator identifier
    attestation_type: Optional[str] = None
    transport: Optional[str] = None  # how the authenticator connects
    name: Optional[str] = None
    created_at: datetime.datetime = datetime.timezone.utc
    last_used_at: datetime.datetime = datetime.timezone.utc

class WebauthnCredentialCreate(WebauthnCredentialBase):
    pass

class WebauthnCredentialOut(WebauthnCredentialBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class WebauthnRegistrationOptions(BaseModel):
    rp_name: str  # app name
    rp_id: str    # domain
    user_id: str
    user_name: str
    challenge: bytes
    pubkey_cred_params: List[Dict[str, Any]]
    timeout: Optional[int] = 60000
    attestation: str = "direct"
    authenticator_selection: Optional[Dict[str, Any]] = None

class WebauthnAuthenticationOptions(BaseModel):
    challenge: bytes
    timeout: Optional[int] = 60000
    rp_id: str
    allow_credentials: Optional[List[Dict[str, Any]]] = None
    user_verification: str = "preferred"

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

    model_config = ConfigDict(from_attributes=True)
