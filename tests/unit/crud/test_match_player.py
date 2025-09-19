import datetime

import pytest
from crud.match_player import create_match_player
from models.models import GameMode, Match, MatchPlayer, Player
from schemas.schemas import MatchPlayerCreate


#todo: cos tu nie gra

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


@pytest.fixture
def test_match(db_session, test_player, test_gamemode):
    match = Match(
        game_mode_id=test_gamemode.id,
        creator_id=test_player.id,
        is_ranked=True,
        additional_info="Test match",
        date=datetime.datetime.now()
    )
    db_session.add(match)
    db_session.commit()

    return match


def test_create_match_player(db_session, test_player, test_match):
    match_player_data = MatchPlayerCreate(
        player_id=test_player.id,
        match_id=test_match.id,
        is_winner=True,
        elo_change=25.0
    )
    
    match_player = create_match_player(db_session, match_player_data)
    
    assert match_player.player_id == test_player.id
    assert match_player.match_id == test_match.id
    assert match_player.is_winner is True
    assert match_player.elo_change == 25.0


def test_create_match_player_loser(db_session, test_player, test_match):
    match_player_data = MatchPlayerCreate(
        player_id=test_player.id,
        match_id=test_match.id,
        is_winner=False,
        elo_change=-15.0
    )
    
    match_player = create_match_player(db_session, match_player_data)
    
    assert match_player.player_id == test_player.id
    assert match_player.match_id == test_match.id
    assert match_player.is_winner is False
    assert match_player.elo_change == -15.0


def test_create_match_player_zero_elo_change(db_session, test_player, test_match):
    match_player_data = MatchPlayerCreate(
        player_id=test_player.id,
        match_id=test_match.id,
        is_winner=False,
        elo_change=0.0
    )
    
    match_player = create_match_player(db_session, match_player_data)
    
    assert match_player.elo_change == 0.0
    assert match_player.is_winner is False


def test_create_multiple_match_players(db_session, test_player, test_match):
    player2 = Player(nick="player2", password="testpass", admin=False, judge=False)
    db_session.add(player2)
    db_session.commit()
    
    winner_data = MatchPlayerCreate(
        player_id=test_player.id,
        match_id=test_match.id,
        is_winner=True,
        elo_change=20.0
    )
    
    loser_data = MatchPlayerCreate(
        player_id=player2.id,
        match_id=test_match.id,
        is_winner=False,
        elo_change=-20.0
    )
    
    winner = create_match_player(db_session, winner_data)
    loser = create_match_player(db_session, loser_data)
    
    assert winner.is_winner is True
    assert loser.is_winner is False
    assert winner.match_id == loser.match_id == test_match.id
    assert winner.elo_change == 20.0
    assert loser.elo_change == -20.0


def test_create_match_player_without_commit(db_session, test_player, test_match):
    """Test that create_match_player doesn't commit automatically"""
    match_player_data = MatchPlayerCreate(
        player_id=test_player.id,
        match_id=test_match.id,
        is_winner=True,
        elo_change=15.0
    )
    
    create_match_player(db_session, match_player_data)
    
    db_session.rollback()
    
    match_players = db_session.query(MatchPlayer).all()
    assert len(match_players) == 0