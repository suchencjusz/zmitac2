from app import db
from app.models import Match, Player


def add_player(nickname):
    player = Player(nickname)
    return db.players.insert_one(player.to_dict())

def add_match(player1id=None, player2id=None, who_won=None, date=None,
              multi_game=False, players1=None, players2=None):
    match = Match(
        player1id=player1id,
        player2id=player2id,
        who_won=who_won,
        date=date,
        multi_game=multi_game,
        players1=players1,
        players2=players2
    )
    return db.matches.insert_one(match.to_dict())

def get_all_matches():
    pipeline = [
        {"$sort": {"date": -1}}  
    ]
    return db.matches.aggregate(pipeline)

def get_all_players():
    return db.players.find().sort("nickname")