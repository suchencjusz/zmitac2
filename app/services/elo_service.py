

from models.models import Player


class EloService:
    K_FACTOR_SOLO = 38
    K_FACTOR_TEAM = 24

    @staticmethod
    def calculate_expected_score(player_elo: float, opponent_elo: float) -> float:
        return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))

    @staticmethod
    def calculate_new_elo(current_elo: float, expected_score: float, actual_score: float, is_solo: bool) -> float:
        k_factor = EloService.K_FACTOR_SOLO if is_solo else EloService.K_FACTOR_TEAM

        return current_elo + k_factor * (actual_score - expected_score)

    @staticmethod
    def calculate_elo_changes(
        winners: list[Player], losers: list[Player]
    ) -> tuple[list[tuple[Player, float]], list[tuple[Player, float]]] | None:
        if not winners or not losers:
            raise ValueError("Both winners and losers lists must be non-empty and non-null.")

        if len(winners) != len(losers):
            raise ValueError("Winners and losers lists must have the same length.")

        is_solo = len(winners) == 1 and len(losers) == 1

        winners_avg_elo = sum(player.elo for player in winners) / len(winners)
        losers_avg_elo = sum(player.elo for player in losers) / len(losers)

        winners_expected_score = EloService.calculate_expected_score(winners_avg_elo, losers_avg_elo)
        losers_expected_score = 1 - winners_expected_score

        winners_elos_change = []
        losers_elos_change = []

        for player in winners:
            new_elo = EloService.calculate_new_elo(player.elo, winners_expected_score, 1, is_solo)
            elo_change = new_elo - player.elo
            winners_elos_change.append((player, elo_change))

        for player in losers:
            new_elo = EloService.calculate_new_elo(player.elo, losers_expected_score, 0, is_solo)
            elo_change = new_elo - player.elo
            losers_elos_change.append((player, elo_change))

        return winners_elos_change, losers_elos_change
