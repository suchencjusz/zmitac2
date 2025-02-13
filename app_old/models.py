from datetime import datetime

from bson import ObjectId


class Player:
    def __init__(self, nickname, date=None):
        self.nickname = nickname
        self.date = date or datetime.now()

    def to_dict(self):
        return {"nickname": self.nickname, "date": self.date}


class Match:
    def __init__(
        self,
        player1id=None,
        player2id=None,
        who_won=None,
        date=None,
        multi_game=False,
        players1=None,
        players2=None,
    ):
        self.who_won = who_won
        self.date = date if isinstance(date, datetime) else datetime.now()
        self.multi_game = multi_game

        if multi_game:
            self.players1 = [ObjectId(p) for p in (players1 or [])]
            self.players2 = [ObjectId(p) for p in (players2 or [])]
        else:
            self.player1id = ObjectId(player1id) if player1id else None
            self.player2id = ObjectId(player2id) if player2id else None

    def to_dict(self):
        data = {
            "who_won": self.who_won,
            "date": self.date,
            "multi_game": self.multi_game,
        }
        if self.multi_game:
            data.update({"players1": self.players1, "players2": self.players2})
        else:
            data.update({"player1id": self.player1id, "player2id": self.player2id})
        return data
