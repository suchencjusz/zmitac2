from datetime import datetime

from bson import ObjectId

from app import db
from app.models import Match, Player


def add_player(nickname) -> ObjectId:
    player = Player(nickname)
    return db.players.insert_one(player.to_dict())


def check_player_exists(nickname) -> bool:
    return db.players.find_one({"nickname": nickname}) is not None


def add_match(
    player1id=None,
    player2id=None,
    who_won=None,
    date=None,
    multi_game=False,
    players1=None,
    players2=None,
) -> ObjectId:
    match_datetime = date if date else None

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


def get_all_matches() -> list:
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
                                            "then": {"$in": ["$_id", "$$team1_players"]},
                                            "else": False,
                                        }
                                    },
                                    {
                                        "$cond": {
                                            "if": {"$isArray": "$$team2_players"},
                                            "then": {"$in": ["$_id", "$$team2_players"]},
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
        {"$sort": {"date": -1}},
    ]
    return db.matches.aggregate(pipeline)


def get_all_players() -> list:
    return db.players.find().sort("nickname", 1)


def get_all_player_matches_by_nickname(nickname) -> list:
    player = db.players.find_one({"nickname": nickname})
    if player:
        return get_all_player_matches_by_id(player["_id"])
    return []


def get_all_player_matches_by_id(player_id) -> list:
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"player1id": player_id},
                    {"player2id": player_id},
                    {"players1": player_id},
                    {"players2": player_id},
                ]
            }
        },
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
                                            "then": {"$in": ["$_id", "$$team1_players"]},
                                            "else": False,
                                        }
                                    },
                                    {
                                        "$cond": {
                                            "if": {"$isArray": "$$team2_players"},
                                            "then": {"$in": ["$_id", "$$team2_players"]},
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
        {"$sort": {"date": -1}},
    ]
    return db.matches.aggregate(pipeline)


def get_nemesis_and_victim(nickname):

    #
    # dziekuje chatugpt za pomoc w tym query <3
    #

    player = db.players.find_one({"nickname": nickname})
    if not player:
        return {"nemesis": None, "victim": None}

    pipeline = [
        # Match all games where our player participated
        {
            "$match": {
                "$or": [
                    {"player1id": player["_id"]},
                    {"player2id": player["_id"]},
                    {"players1": player["_id"]},
                    {"players2": player["_id"]},
                ]
            }
        },
        # Lookup player details
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
                                    {"$in": ["$_id", "$$team1_players"]},
                                    {"$in": ["$_id", "$$team2_players"]},
                                ]
                            }
                        }
                    }
                ],
                "as": "players",
            }
        },
        # Unwind players array
        {"$unwind": "$players"},
        # Remove self from opponents
        {"$match": {"players.nickname": {"$ne": nickname}}},
        # Group by opponent and calculate stats
        {
            "$group": {
                "_id": "$players.nickname",
                "total_matches": {"$sum": 1},
                "lost_against": {
                    "$sum": {
                        "$switch": {
                            "branches": [
                                # Single player matches
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", False]},
                                            {"$eq": ["$player1id", player["_id"]]},
                                            {"$eq": ["$who_won", "player2"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", False]},
                                            {"$eq": ["$player2id", player["_id"]]},
                                            {"$eq": ["$who_won", "player1"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                                # Team matches
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", True]},
                                            {"$in": [player["_id"], "$players1"]},
                                            {"$eq": ["$who_won", "players2"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", True]},
                                            {"$in": [player["_id"], "$players2"]},
                                            {"$eq": ["$who_won", "players1"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                            ],
                            "default": 0,
                        }
                    }
                },
                "won_against": {
                    "$sum": {
                        "$switch": {
                            "branches": [
                                # Single player matches
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", False]},
                                            {"$eq": ["$player1id", player["_id"]]},
                                            {"$eq": ["$who_won", "player1"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", False]},
                                            {"$eq": ["$player2id", player["_id"]]},
                                            {"$eq": ["$who_won", "player2"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                                # Team matches
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", True]},
                                            {"$in": [player["_id"], "$players1"]},
                                            {"$eq": ["$who_won", "players1"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", True]},
                                            {"$in": [player["_id"], "$players2"]},
                                            {"$eq": ["$who_won", "players2"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                            ],
                            "default": 0,
                        }
                    }
                },
            }
        },
    ]

    results = list(db.matches.aggregate(pipeline))
    if not results:
        return {"nemesis": None, "victim": None}

    # Find nemesis (opponent with most wins against us)
    nemesis = max(results, key=lambda x: (x["lost_against"], x["total_matches"]), default=None)
    # Find victim (opponent we beat the most)
    victim = max(results, key=lambda x: (x["won_against"], x["total_matches"]), default=None)

    return {
        "nemesis": (
            {
                "nickname": nemesis["_id"],
                "losses": nemesis["lost_against"],
                "total": nemesis["total_matches"],
            }
            if nemesis and nemesis["lost_against"] > 0
            else None
        ),
        "victim": (
            {
                "nickname": victim["_id"],
                "wins": victim["won_against"],
                "total": victim["total_matches"],
            }
            if victim and victim["won_against"] > 0
            else None
        ),
    }


def get_top_opponents(nickname, limit=5):
    player = db.players.find_one({"nickname": nickname})
    if not player:
        return None

    pipeline = [
        # Match all games where our player participated
        {
            "$match": {
                "$or": [
                    {"player1id": player["_id"]},
                    {"player2id": player["_id"]},
                    {"players1": player["_id"]},
                    {"players2": player["_id"]},
                ]
            }
        },
        # Lookup player details
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
                                    {"$in": ["$_id", "$$team1_players"]},
                                    {"$in": ["$_id", "$$team2_players"]},
                                ]
                            }
                        }
                    }
                ],
                "as": "players",
            }
        },
        # Unwind players array
        {"$unwind": "$players"},
        # Remove self from opponents
        {"$match": {"players.nickname": {"$ne": nickname}}},
        # Group by opponent and count games together
        {"$group": {"_id": "$players.nickname", "games_together": {"$sum": 1}}},
        # Sort by number of games descending
        {"$sort": {"games_together": -1}},
        # Limit results
        {"$limit": limit},
    ]

    return list(db.matches.aggregate(pipeline))


def get_player_matches_data_by_nickname(nickname) -> dict:
    if not check_player_exists(nickname):
        return {}

    player_all_matches = list(get_all_player_matches_by_nickname(nickname))
    top_opponents = get_top_opponents(nickname)
    nemesis_victim = get_nemesis_and_victim(nickname)

    matches_count = len(player_all_matches)
    wins_count = 0
    losses_count = 0
    draws_count = 0
    last_match_date = None
    last_match_who_won = None
    last_match_opponent = None

    # basic win/loss/draw stats with ratio
    if matches_count > 0:
        for match in player_all_matches:
            if match["multi_game"]:
                player_obj = next((p for p in match["players"] if p["nickname"] == nickname), None)
                if player_obj:
                    player_id = player_obj["_id"]
                    if match["who_won"] == "draw":
                        draws_count += 1
                    elif player_id in match["players1"] and match["who_won"] == "players1":
                        wins_count += 1
                    elif player_id in match["players2"] and match["who_won"] == "players2":
                        wins_count += 1
                    elif match["who_won"] != "none":
                        losses_count += 1
            else:
                player_obj = next((p for p in match["players"] if p["nickname"] == nickname), None)
                if player_obj:
                    player_id = player_obj["_id"]
                    if match["who_won"] == "draw":
                        draws_count += 1
                    elif (match["player1id"] == player_id and match["who_won"] == "player1") or (
                        match["player2id"] == player_id and match["who_won"] == "player2"
                    ):
                        wins_count += 1
                    elif match["who_won"] != "none":
                        losses_count += 1

    # last game check
    if matches_count > 0:
        last_match = player_all_matches[0]
        last_match_date = last_match["date"]

        current_player_obj = next((p for p in last_match["players"] if p["nickname"] == nickname), None)

        if last_match["multi_game"]:
            if current_player_obj:
                current_player_id = current_player_obj["_id"]
                if last_match["who_won"] == "players1" and current_player_id in last_match["players1"]:
                    last_match_who_won = nickname
                elif last_match["who_won"] == "players2" and current_player_id in last_match["players2"]:
                    last_match_who_won = nickname
                else:
                    winning_team = (
                        last_match["players1"] if last_match["who_won"] == "players1" else last_match["players2"]
                    )
                    opponent = next(
                        (
                            p["nickname"]
                            for p in last_match["players"]
                            if p["_id"] in winning_team and p["nickname"] != nickname
                        ),
                        None,
                    )
                    last_match_who_won = opponent
        else:
            if current_player_obj:
                current_player_id = current_player_obj["_id"]
                if (last_match["who_won"] == "player1" and last_match["player1id"] == current_player_id) or (
                    last_match["who_won"] == "player2" and last_match["player2id"] == current_player_id
                ):
                    last_match_who_won = nickname
                else:
                    if last_match["who_won"] == "player1":
                        last_match_who_won = next(
                            (p["nickname"] for p in last_match["players"] if p["_id"] == last_match["player1id"]),
                            None,
                        )
                    else:
                        last_match_who_won = next(
                            (p["nickname"] for p in last_match["players"] if p["_id"] == last_match["player2id"]),
                            None,
                        )

        last_match_opponent = next(
            (p["nickname"] for p in last_match["players"] if p["nickname"] != nickname),
            None,
        )

    win_ratio = round(wins_count / matches_count * 100, 2) if matches_count > 0 else 0

    return {
        "nickname": nickname,
        "matches_count": matches_count,
        "wins_count": wins_count,
        "losses_count": losses_count,
        "draws_count": draws_count,
        "win_ratio": win_ratio,
        "top_opponents": top_opponents,
        "last_match_date": last_match_date,
        "last_match_who_won": last_match_who_won,
        "last_match_opponent": last_match_opponent,
        "nemesis": nemesis_victim["nemesis"],
        "victim": nemesis_victim["victim"],
    }


def get_players_with_best_win_ratio(limit=5):
    pipeline = [
        # Match all games
        {
            "$match": {
                "$or": [
                    {"player1id": {"$exists": True}},
                    {"players1": {"$exists": True}},
                ]
            }
        },
        # Lookup player details
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
                                    {"$in": ["$_id", "$$team1_players"]},
                                    {"$in": ["$_id", "$$team2_players"]},
                                ]
                            }
                        }
                    }
                ],
                "as": "players",
            }
        },
        {"$unwind": "$players"},
        {
            "$group": {
                "_id": "$players.nickname",
                "total_matches": {"$sum": 1},
                "wins": {
                    "$sum": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", False]},
                                            {"$eq": ["$who_won", "player1"]},
                                            {"$eq": ["$player1id", "$players._id"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", False]},
                                            {"$eq": ["$who_won", "player2"]},
                                            {"$eq": ["$player2id", "$players._id"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", True]},
                                            {"$eq": ["$who_won", "players1"]},
                                            {"$in": ["$players._id", "$players1"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$eq": ["$multi_game", True]},
                                            {"$eq": ["$who_won", "players2"]},
                                            {"$in": ["$players._id", "$players2"]},
                                        ]
                                    },
                                    "then": 1,
                                },
                            ],
                            "default": 0,
                        }
                    }
                },
            }
        },
        {"$match": {"total_matches": {"$gt": 0}}},
    ]

    results = list(db.matches.aggregate(pipeline))

    # Calculate win ratio and sort
    for player in results:
        player["win_ratio"] = round((player["wins"] / player["total_matches"]) * 100, 2)
        player["nickname"] = player["_id"]

    sorted_results = sorted(results, key=lambda x: (-x["win_ratio"], -x["total_matches"]))[:limit]

    return sorted_results
