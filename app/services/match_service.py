from crud.match import create_match
from crud.player import get_player_by_id, update_player_elo
from crud.match_player import create_match_player

from schemas.schemas import MatchCreate, MatchPlayerCreate
from services.elo_service import EloService


class MatchService:

    #
    # logika meczowa, transkacja sql
    #
    
    @staticmethod
    def process_match(db, match_data: MatchCreate):
        try:
            # 1. Walidacja - pobierz graczy
            winners = [
                get_player_by_id(db, pid) for pid in match_data.players_ids_winners
            ]
            losers = [
                get_player_by_id(db, pid) for pid in match_data.players_ids_losers
            ]

            if None in winners or None in losers:
                raise ValueError("Jeden lub więcej graczy nie istnieje w bazie")

            # 2. Oblicz zmiany ELO TYLKO dla meczy rankingowych
            if match_data.is_ranked:
                elo_changes = EloService.calculate_elo_changes(winners, losers)

                if elo_changes is None:
                    raise ValueError("Nie udało się obliczyć zmian ELO")

                winners_elos_change, losers_elos_change = elo_changes
            else:
                # Dla nierankingowych meczy, zmiana ELO = 0
                winners_elos_change = [(player, 0) for player in winners]
                losers_elos_change = [(player, 0) for player in losers]

            # 3. Utwórz rekord meczu (bez commit)
            match_record = create_match(db, match_data, commit=False)

            # 4. Aktualizuj ELO zwycięzców (bez commit)
            for player, elo_change in winners_elos_change:
                if match_data.is_ranked:
                    new_elo = player.elo + elo_change
                    update_player_elo(db, player, new_elo, commit=False)

                create_match_player(
                    db,
                    MatchPlayerCreate(
                        match_id=match_record.id,
                        player_id=player.id,
                        is_winner=True,
                        elo_change=elo_change,
                    ),
                    commit=False,
                )

            # 5. Aktualizuj ELO przegranych (bez commit)
            for player, elo_change in losers_elos_change:
                if match_data.is_ranked:
                    new_elo = player.elo + elo_change
                    update_player_elo(db, player, new_elo, commit=False)

                create_match_player(
                    db,
                    MatchPlayerCreate(
                        match_id=match_record.id,
                        player_id=player.id,
                        is_winner=False,
                        elo_change=elo_change,
                    ),
                    commit=False,
                )

            # 6. Commituj WSZYSTKIE zmiany naraz
            db.commit()
            return match_record

        except Exception as e:
            # Wycofaj wszystkie zmiany w przypadku błędu
            db.rollback()
            raise e
