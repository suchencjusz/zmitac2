import datetime

import pytest
from crud.match import create_match, get_all_matches, get_match_by_id
from models.models import GameMode, Match, Player
from schemas.schemas import MatchCreate


@pytest.fixture
def test_player(db_session):
    player = Player(nick="testplayer", password="testpass", admin=False, judge=False)
    db_session.add(player)
    db_session.commit()
    return player


@pytest.fixture
def test_gamemode(db_session):
    gamemode = GameMode(name="8-ball", description="Standard 8-ball pool")
    db_session.add(gamemode)
    db_session.commit()
    return gamemode


def test_create_match(db_session, test_player, test_gamemode):
    match_data = MatchCreate(
        date=datetime.datetime.now(),
        is_ranked=True,
        additional_info="Test match",
        game_mode_id=test_gamemode.id,
        creator_id=test_player.id,
        players_ids_winners=[test_player.id],
        players_ids_losers=[]
    )
    
    match = create_match(db_session, match_data)
    
    assert match.id is not None
    assert match.is_ranked is True
    assert match.additional_info == "Test match"
    assert match.game_mode_id == test_gamemode.id
    assert match.creator_id == test_player.id


def test_get_match_by_id(db_session, test_player, test_gamemode):
    match_data = MatchCreate(
        date=datetime.datetime.now(),
        is_ranked=False,
        additional_info="Another test match",
        game_mode_id=test_gamemode.id,
        creator_id=test_player.id,
        players_ids_winners=[test_player.id],
        players_ids_losers=[]
    )
    
    created_match = create_match(db_session, match_data)
    db_session.commit()
    
    retrieved_match = get_match_by_id(db_session, created_match.id)
    
    assert retrieved_match is not None
    assert retrieved_match.id == created_match.id
    assert retrieved_match.is_ranked is False
    assert retrieved_match.additional_info == "Another test match"


def test_get_nonexistent_match(db_session):
    match = get_match_by_id(db_session, 999)
    
    assert match is None


def test_get_all_matches(db_session, test_player, test_gamemode):
    match_data1 = MatchCreate(
        date=datetime.datetime.now(),
        is_ranked=True,
        additional_info="Match 1",
        game_mode_id=test_gamemode.id,
        creator_id=test_player.id,
        players_ids_winners=[test_player.id],
        players_ids_losers=[]
    )
    
    match_data2 = MatchCreate(
        date=datetime.datetime.now(),
        is_ranked=False,
        additional_info="Match 2",
        game_mode_id=test_gamemode.id,
        creator_id=test_player.id,
        players_ids_winners=[test_player.id],
        players_ids_losers=[]
    )
    
    create_match(db_session, match_data1)
    create_match(db_session, match_data2)
    db_session.commit()
    
    matches = get_all_matches(db_session)

    assert len(matches) == 2


def test_create_match_with_minimal_data(db_session, test_player, test_gamemode):
    match_data = MatchCreate(
        game_mode_id=test_gamemode.id,
        creator_id=test_player.id,
        players_ids_winners=[test_player.id],
        players_ids_losers=[]
    )
    
    match = create_match(db_session, match_data)
    
    assert match.id is not None
    assert match.is_ranked is True
    assert match.additional_info is None
    assert match.date is not None