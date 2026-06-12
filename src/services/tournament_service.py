from datetime import datetime

class TournamentService:
    def __init__(self, tournament_repository):
        self.tournament_repository = tournament_repository

    def create_tournament(self, name, description, game_id, max_teams, start_date, end_date):
        if not name:
            raise ValueError("Tournament name is required")

        if max_teams not in (8, 16):
            raise ValueError("Max teams must be 8 or 16")

        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

        return self.tournament_repository.create(
            name=name,
            description=description,
            game_id=game_id,
            max_teams=max_teams,
            start_date=start_date,
            end_date=end_date,
            status="Draft"
        )