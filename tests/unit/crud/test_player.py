import pytest
from crud.player import (
    create_player,
    delete_player,
    get_all_players,
    get_player_by_id,
    get_player_by_nick,
    update_player_elo,
)
from schemas.schemas import PlayerCreate


def test_create_basic_player(db_session):
    player = create_player(db_session, PlayerCreate(nick="bob", password="test123"))

    assert player.id is not None
    assert player.admin is False
    assert player.judge is False
    assert player.nick == "bob"
    assert player.elo == 1000.0


def test_get_nonexistent_player(db_session):
    player = get_player_by_id(db_session, 999)
    assert player is None


def test_get_existing_player(db_session):
    created = create_player(db_session, PlayerCreate(nick="alice", password="test123"))
    fetched = get_player_by_id(db_session, created.id)
    assert fetched.nick == "alice"


def test_get_player_by_nick(db_session):
    create_player(db_session, PlayerCreate(nick="alice", password="test"))
    player = get_player_by_nick(db_session, "alice")
    assert player.nick == "alice"


def test_list_players(db_session):
    create_player(db_session, PlayerCreate(nick="player1", password="test"))
    create_player(db_session, PlayerCreate(nick="player2", password="test"))
    players = get_all_players(db_session)
    assert len(players) == 2


def test_delete_player_success(db_session):
    player = create_player(db_session, PlayerCreate(nick="todelete", password="test123"))
    delete_player(db_session, player.id)
    assert get_player_by_id(db_session, player.id) is None


# special cases
def test_create_admin_player(db_session):
    player = create_player(db_session, PlayerCreate(nick="admin", password="test123", admin=True))
    assert player.admin is True


def test_create_judge_player(db_session):
    player = create_player(db_session, PlayerCreate(nick="judge", password="test123", judge=True))
    assert player.judge is True


def test_create_player_with_custom_elo(db_session):
    player = create_player(db_session, PlayerCreate(nick="pro", password="test123", elo=2000.0))
    assert player.elo == 2000.0


def test_create_player_duplicate_nick(db_session):
    create_player(db_session, PlayerCreate(nick="unique", password="test123"))
    with pytest.raises(Exception):
        create_player(db_session, PlayerCreate(nick="unique", password="test456"))


def test_update_player_elo_negative(db_session):
    player = create_player(db_session, PlayerCreate(nick="neg_elo", password="test123"))

    updated_player = update_player_elo(db_session, player, -500)
    assert updated_player.elo == 0.0


def test_update_player_elo_valid(db_session):
    player = create_player(db_session, PlayerCreate(nick="valid_elo", password="test123"))

    updated_player = update_player_elo(db_session, player, 1500.5)
    assert updated_player.elo == 1500.5
