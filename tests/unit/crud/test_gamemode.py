import pytest
from crud.game_mode import create_game_mode, get_game_mode, get_game_modes, update_game_mode
from models.models import GameMode


def test_create_basic_game_mode(db_session):
    game_mode = create_game_mode(db_session, GameMode(name="standard", description="standard description"))
    assert game_mode.id is not None
    assert game_mode.name == "standard"
    assert game_mode.description == "standard description"

def test_get_nonexistent_game_mode(db_session):
    game_mode = get_game_mode(db_session, 999)
    assert game_mode is None

def test_get_existing_game_mode(db_session):
    created = create_game_mode(db_session, GameMode(name="standard", description="standard description"))
    fetched = get_game_mode(db_session, created.id)
    assert fetched.name == "standard"

def test_list_game_modes(db_session):
    create_game_mode(db_session, GameMode(name="standard", description="standard description"))
    create_game_mode(db_session, GameMode(name="custom", description="custom description"))
    game_modes = get_game_modes(db_session)
    assert len(game_modes) == 2

def test_update_game_mode(db_session):
    game_mode = create_game_mode(db_session, GameMode(name="standard", description="standard description"))
    updated = update_game_mode(db_session, game_mode.id, GameMode(name="custom", description="custom description"))
    
    assert updated.name == "custom"
    assert updated.description == "custom description"
    assert updated.id == game_mode.id
    