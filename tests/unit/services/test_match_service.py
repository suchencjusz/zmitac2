import pytest

from models.models import GameMode
from schemas.schemas import MatchCreate, PlayerCreate

from crud.player import (
    create_player,
    get_player_by_id,
)

from services.match_service import MatchService
import datetime


@pytest.fixture
def create_test_players(db_session):
    p1 = create_player(db_session, PlayerCreate(nick="arek", password="test123"))
    p2 = create_player(db_session, PlayerCreate(nick="bartek", password="test123"))
    p3 = create_player(db_session, PlayerCreate(nick="celina", password="test123"))
    p4 = create_player(db_session, PlayerCreate(nick="daniel", password="test123"))
    p5 = create_player(db_session, PlayerCreate(nick="ewa", password="test123"))

    return [p1, p2, p3, p4, p5]


@pytest.fixture
def create_test_gamemodes(db_session):
    gm1 = GameMode(name="8-ball", description="Standardowy bilard")
    gm2 = GameMode(name="9-ball", description="Cuda babilonskie")

    db_session.add(gm1)
    db_session.add(gm2)
    db_session.commit()

    return [gm1, gm2]


def test_1v1_unranked_match(db_session, create_test_players, create_test_gamemodes):
    players = create_test_players
    gamemodes = create_test_gamemodes

    match_data = MatchCreate(
        date=datetime.datetime.now(),
        is_ranked=False,
        additional_info="Test unranked 1v1 match",
        game_mode_id=gamemodes[0].id,
        creator_id=players[0].id,
        players_ids_winners=[players[0].id],
        players_ids_losers=[players[1].id],
    )

    MatchService.process_match(db_session, match_data)

    p1 = get_player_by_id(db_session, players[0].id)
    p2 = get_player_by_id(db_session, players[1].id)

    assert p1.elo == 1000.0
    assert p2.elo == 1000.0


def test_1v1_ranked_match(db_session, create_test_players, create_test_gamemodes):
    players = create_test_players
    gamemodes = create_test_gamemodes

    match_data = MatchCreate(
        date=datetime.datetime.now(),
        is_ranked=True,
        additional_info="Test ranked 1v1 match",
        game_mode_id=gamemodes[0].id,
        creator_id=players[0].id,
        players_ids_winners=[players[0].id],
        players_ids_losers=[players[1].id],
    )

    MatchService.process_match(db_session, match_data)

    p1 = get_player_by_id(db_session, players[0].id)
    p2 = get_player_by_id(db_session, players[1].id)

    assert (p1.elo - 1000.0) == 19.0
    assert (p2.elo - 1000.0) == -19.0


def test_2v2_unranked_match(db_session, create_test_players, create_test_gamemodes):
    players = create_test_players
    gamemode = create_test_gamemodes

    p1, p2, p3, p4, p5 = players
    gamemode = gamemode[0]

    match_data = MatchCreate(
        date=datetime.datetime.now(),
        is_ranked=False,
        additional_info="Test unranked 2v2 match",
        game_mode_id=gamemode.id,
        creator_id=p1.id,
        players_ids_winners=[p1.id, p2.id],
        players_ids_losers=[p3.id, p4.id],
    )

    MatchService.process_match(db_session, match_data)

    p1 = get_player_by_id(db_session, p1.id)
    p2 = get_player_by_id(db_session, p2.id)
    p3 = get_player_by_id(db_session, p3.id)
    p4 = get_player_by_id(db_session, p4.id)

    assert p1.elo == 1000.0
    assert p2.elo == 1000.0
    assert p3.elo == 1000.0
    assert p4.elo == 1000.0
    assert p5.elo == 1000.0


def test_2v2_ranked_match(db_session, create_test_players, create_test_gamemodes):
    players = create_test_players
    gamemode = create_test_gamemodes

    p1, p2, p3, p4, p5 = players
    gamemode = gamemode[0]

    match_data = MatchCreate(
        date=datetime.datetime.now(),
        is_ranked=True,
        additional_info="Test ranked 2v2 match",
        game_mode_id=gamemode.id,
        creator_id=p1.id,
        players_ids_winners=[p1.id, p2.id],
        players_ids_losers=[p3.id, p4.id],
    )

    MatchService.process_match(db_session, match_data)

    p1 = get_player_by_id(db_session, p1.id)
    p2 = get_player_by_id(db_session, p2.id)
    p3 = get_player_by_id(db_session, p3.id)
    p4 = get_player_by_id(db_session, p4.id)

    assert (p1.elo - 1000.0) == 12.0
    assert (p2.elo - 1000.0) == 12.0
    assert (p3.elo - 1000.0) == -12.0
    assert (p4.elo - 1000.0) == -12.0
    assert p5.elo == 1000.0

def test_none_vs_none_match(db_session, create_test_players, create_test_gamemodes):
    players = create_test_players
    gamemode = create_test_gamemodes

    p1, p2, p3, p4, p5 = players
    gamemode = gamemode[0]

    match_data = MatchCreate(
        date=datetime.datetime.now(),
        is_ranked=True,
        additional_info="Test ranked none vs none match",
        game_mode_id=gamemode.id,
        creator_id=p1.id,
        players_ids_winners=[],
        players_ids_losers=[],
    )

    with pytest.raises(ValueError):
        MatchService.process_match(db_session, match_data)

# defacto pydantic to lapie
# def test_none_vs_none_match_2(db_session, create_test_players, create_test_gamemodes):
#     players = create_test_players
#     gamemode = create_test_gamemodes
#
#     p1, p2, p3, p4, p5 = players
#     gamemode = gamemode[0]
#
#     match_data = MatchCreate(
#         date=datetime.datetime.now(),
#         is_ranked=True,
#         additional_info="Test ranked none vs none match",
#         game_mode_id=gamemode.id,
#         creator_id=None,
#         players_ids_winners=[p1.id, p2.id],
#         players_ids_losers=[p3.id, p4.id],
#     )
#
#     with pytest.raises:
#         MatchService.process_match(db_session, match_data)
