from datetime import datetime

from bson import ObjectId


class Player:
    def __init__(self, nickname, date=None):
        self.nickname = nickname
        self.date = date or datetime.now()

    def to_dict(self):
        return {
            "nickname": self.nickname,
            "date": self.date
        }

class Match:
    def __init__(
        self,
        player1id=None,
        player2id=None,
        who_won=None,
        date=None,
        multi_game=False,
        players1=None,
        players2=None
    ):
        self.who_won = who_won or "none"
        self.date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()

        if multi_game:
            self.multi_game = True
            self.players1 = [ObjectId(p) for p in players1 or []]
            self.players2 = [ObjectId(p) for p in players2 or []]
        else:
            # single game
            self.multi_game = False
            self.player1id = ObjectId(player1id)
            self.player2id = ObjectId(player2id)

    def to_dict(self):
        data = {
            "who_won": self.who_won,
            "date": self.date,
            "multi_game": self.multi_game
        }
        if self.multi_game:
            data["players1"] = self.players1
            data["players2"] = self.players2
        else:
            data["player1id"] = self.player1id
            data["player2id"] = self.player2id
        
        return data