from datetime import datetime

from bson import ObjectId

from app import db
from app.models import Match, Player


def add_player(nickname):
    player = Player(nickname)
    return db.players.insert_one(player.to_dict())


def add_match(
    player1id=None,
    player2id=None,
    who_won=None,
    date=None,
    time=None,
    multi_game=False,
    players1=None,
    players2=None,
):
    if date and time:
        match_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    elif date:
        match_datetime = datetime.strptime(date, "%Y-%m-%d")
    else:
        match_datetime = datetime.now()

    match = Match(
        player1id=player1id,
        player2id=player2id,
        who_won=who_won,
        date=match_datetime,
        multi_game=multi_game,
        players1=players1,
        players2=players2,
    )
    return db.matches.insert_one(match.to_dict())


def get_all_matches():
    pipeline = [
        {
            "$lookup": {
                "from": "players",
                "let": {
                    "player1_id": "$player1id",
                    "player2_id": "$player2id",
                    "team1_players": {"$ifNull": ["$players1", []]},
                    "team2_players": {"$ifNull": ["$players2", []]},
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$or": [
                                    {"$eq": ["$_id", "$$player1_id"]},
                                    {"$eq": ["$_id", "$$player2_id"]},
                                    {
                                        "$cond": {
                                            "if": {"$isArray": "$$team1_players"},
                                            "then": {
                                                "$in": ["$_id", "$$team1_players"]
                                            },
                                            "else": False,
                                        }
                                    },
                                    {
                                        "$cond": {
                                            "if": {"$isArray": "$$team2_players"},
                                            "then": {
                                                "$in": ["$_id", "$$team2_players"]
                                            },
                                            "else": False,
                                        }
                                    },
                                ]
                            }
                        }
                    }
                ],
                "as": "players",
            }
        },
        {"$sort": {"datetime": -1}},
    ]
    return db.matches.aggregate(pipeline)


def get_all_players():
    return db.players.find().sort("nickname")
