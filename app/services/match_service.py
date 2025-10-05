
from crud.match import create_match
from crud.player import get_player_by_id, update_player_elo
from schemas.schemas import MatchCreate
from services.elo_service import EloService


class MatchService:
    @staticmethod
    def process_match(db, match_data: MatchCreate) -> None:
        """
        Process a match with full transaction support.
        If anything fails, all changes are rolled back.
        """
        try:
            # Start transaction (already started by SQLAlchemy session)
            winners = [get_player_by_id(db, player_id) for player_id in match_data.winner_ids]
            losers = [get_player_by_id(db, player_id) for player_id in match_data.loser_ids]

            # Calculate ELO changes
            elo_changes = EloService.calculate_elo_changes(winners, losers)

            if elo_changes is None:
                db.rollback()
                raise ValueError("Could not calculate ELO changes")

            winners_elos_change, losers_elos_change = elo_changes

            # Update player ELO ratings
            for player, elo_change in winners_elos_change + losers_elos_change:
                player.elo += elo_change
                update_player_elo(db, player, player.elo)

            # Create the match record
            match_record = create_match(db, match_data)

            # Create match-player relationships
            # Winners
            for player in winners:
                create_match_player(db, match_record.id, player.id, won=True)

            # Losers
            for player in losers:
                create_match_player(db, match_record.id, player.id, won=False)

            # Commit all changes
            db.commit()
            return match_record

        except Exception as e:
            # Rollback all changes if anything goes wrong
            db.rollback()
            raise e
