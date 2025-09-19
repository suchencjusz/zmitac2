#
# tested with https://www.omnicalculator.com/sports/elo
#

import pytest
from models.models import Player
from services.elo_service import EloService


class TestEloService:

    def test_calculate_expected_score_equal_players(self):
        """Test: Gracze o równym ELO mają expected score = 0.5"""

        expected = EloService.calculate_expected_score(1000, 1000)

        assert expected == 0.5

    def test_calculate_expected_score_stronger_player(self):
        """Test: Silniejszy gracz ma wyższy expected score"""

        expected = EloService.calculate_expected_score(1200, 1000)

        assert expected > 0.5
        assert expected < 1.0

    def test_calculate_expected_score_weaker_player(self):
        """Test: Słabszy gracz ma niższy expected score"""

        expected = EloService.calculate_expected_score(1000, 1200)

        assert expected < 0.5
        assert expected > 0.0

    def test_calculate_new_elo_solo_win(self):
        # sprawdzone

        """Test: Wygrana w solo - ELO rośnie"""

        current_elo = 1000
        expected_score = 0.5  # rowny przeciwnik
        actual_score = 1.0  # wygrana

        new_elo = EloService.calculate_new_elo(current_elo, expected_score, actual_score, is_solo=True)

        assert new_elo == 1019

    def test_calculate_new_elo_solo_loss(self):
        # sprawdzone

        """Test: Przegrana w solo - ELO spada"""

        current_elo = 1000
        expected_score = 0.5  # rowny przeciwnik
        actual_score = 0.0  # przegrana

        new_elo = EloService.calculate_new_elo(current_elo, expected_score, actual_score, is_solo=True)

        assert new_elo == 981

    def test_calculate_new_elo_team_vs_solo_k_factor(self):
        # sprawdzone

        """Test: Mecze teamowe mają mniejszy K_FACTOR niż solo"""

        current_elo = 1000
        expected_score = 0.5
        actual_score = 1.0

        solo_elo = EloService.calculate_new_elo(current_elo, expected_score, actual_score, is_solo=True)
        team_elo = EloService.calculate_new_elo(current_elo, expected_score, actual_score, is_solo=False)

        solo_change = solo_elo - current_elo  # Powinno być +19 (K=38)
        team_change = team_elo - current_elo  # Powinno być +12 (K=24)

        assert solo_change > team_change
        assert solo_change == 19
        assert team_change == 12

    def test_calculate_elo_changes_solo_match(self):
        # sprawdzone

        """Test: Mecz solo 1vs1 z prawdziwymi Player obiektami"""

        winner = Player(nick="Arek", elo=1200.0)
        loser = Player(nick="Bartek", elo=1000.0)

        winners_changes, losers_changes = EloService.calculate_elo_changes([winner], [loser])

        assert len(winners_changes) == 1
        assert len(losers_changes) == 1

        winner_player, winner_change = winners_changes[0]
        loser_player, loser_change = losers_changes[0]

        assert winner_player == winner
        assert loser_player == loser
        assert isinstance(winner_player, Player)

        assert winner_change > 0
        assert loser_change < 0

        # zero-sum (suma zmian = 0)
        total_change = winner_change + loser_change

        assert abs(total_change) < 0.01

    def test_calculate_elo_changes_team_match(self):
        # sprawdzone

        """Test: Mecz drużynowy 2vs2 - sprawdź konkretne zmiany ELO"""

        team_a = [Player(nick="Gracz1", elo=1100.0), Player(nick="Gracz2", elo=1300.0)]  # Avg: 1200
        team_b = [Player(nick="Gracz3", elo=1150.0), Player(nick="Gracz4", elo=1250.0)]  # Avg: 1200

        winners_changes, losers_changes = EloService.calculate_elo_changes(team_a, team_b)

        assert len(winners_changes) == 2
        assert len(losers_changes) == 2

        winner_players = [player for player, _ in winners_changes]
        assert all(player in team_a for player in winner_players)

        loser_players = [player for player, _ in losers_changes]
        assert all(player in team_b for player in loser_players)

        gracz1_change = None
        gracz2_change = None
        gracz3_change = None
        gracz4_change = None

        for player, change in winners_changes:
            if player.nick == "Gracz1":
                gracz1_change = change
            elif player.nick == "Gracz2":
                gracz2_change = change

        for player, change in losers_changes:
            if player.nick == "Gracz3":
                gracz3_change = change
            elif player.nick == "Gracz4":
                gracz4_change = change

        assert gracz1_change is not None
        assert gracz2_change is not None
        assert gracz3_change is not None
        assert gracz4_change is not None

        assert gracz1_change > 0, f"Gracz1 powinien zyskać punkty, ale ma {gracz1_change}"
        assert gracz2_change > 0, f"Gracz2 powinien zyskać punkty, ale ma {gracz2_change}"

        assert gracz3_change < 0, f"Gracz3 powinien stracić punkty, ale ma {gracz3_change}"
        assert gracz4_change < 0, f"Gracz4 powinien stracić punkty, ale ma {gracz4_change}"

        expected_change = 12.0  # https://www.omnicalculator.com/sports/elo

        assert abs(gracz1_change - expected_change) < 0.01
        assert abs(gracz2_change - expected_change) < 0.01
        assert abs(gracz3_change - (-expected_change)) < 0.01
        assert abs(gracz4_change - (-expected_change)) < 0.01

        # zero-sum
        total_winner_changes = sum(change for _, change in winners_changes)
        total_loser_changes = sum(change for _, change in losers_changes)
        total_change = total_winner_changes + total_loser_changes

        assert abs(total_change) < 0.01

    def test_elo_realistic_scenario(self):
        # sprawdzone

        """Test: Realistyczny scenariusz - słabszy gracz wygrywa z silniejszym"""

        weak_player = Player(nick="Słaby", elo=800.0)
        strong_player = Player(nick="Silny", elo=1400.0)

        winners_changes, losers_changes = EloService.calculate_elo_changes([weak_player], [strong_player])

        weak_change = winners_changes[0][1]
        strong_change = losers_changes[0][1]

        # assert weak_change > 30
        # assert strong_change < -30

        assert weak_change > 36 and weak_change < 37
        assert strong_change < -36 and strong_change > -37

        # zero-sum
        assert abs(weak_change + strong_change) < 0.01

    def test_empty_teams_should_fail(self):
        """Test: Puste drużyny powinny wywołać błąd"""

        player = Player(nick="Solo", elo=1000.0)

        with pytest.raises(ValueError):
            EloService.calculate_elo_changes([], [player])

        with pytest.raises(ValueError):
            EloService.calculate_elo_changes([player], [])
