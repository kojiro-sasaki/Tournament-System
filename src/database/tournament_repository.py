from database.connection import supabase


class TournamentRepository:

    TOURNAMENT_FIELDS = (
        'id, game_id, name, description, start_date, '
        'end_date, status, max_teams, created_by'
    )


    @staticmethod
    def get_all():
        return (
            supabase
            .table('tournaments')
            .select(TournamentRepository.TOURNAMENT_FIELDS)
            .execute()
        )


    @staticmethod
    def get_by_id(tournament_id: int):
        return (
            supabase
            .table('tournaments')
            .select(TournamentRepository.TOURNAMENT_FIELDS)
            .eq('id', tournament_id)
            .single()
            .execute()
        )


    @staticmethod
    def get_by_game(game_id: int):
        return (
            supabase
            .table('tournaments')
            .select(TournamentRepository.TOURNAMENT_FIELDS)
            .eq('game_id', game_id)
            .execute()
        )


    @staticmethod
    def get_by_name(name: str):
        return (
            supabase
            .table('tournaments')
            .select(TournamentRepository.TOURNAMENT_FIELDS)
            .eq('name', name)
            .single()
            .execute()
        )


    @staticmethod
    def create(data: dict):
        return (
            supabase
            .table('tournaments')
            .insert(data)
            .execute()
        )


    @staticmethod
    def update_by_id(
        tournament_id: int,
        data: dict
    ):
        allowed_fields = {
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'max_teams'
        }

        filtered_data = {
            key: value
            for key, value in data.items()
            if key in allowed_fields
        }

        if not filtered_data:
            raise ValueError(
                'No valid fields provided for update'
            )

        return (
            supabase
            .table('tournaments')
            .update(filtered_data)
            .eq('id', tournament_id)
            .execute()
        )


    @staticmethod
    def delete_by_id(tournament_id: int):
        return (
            supabase
            .table('tournaments')
            .delete()
            .eq('id', tournament_id)
            .execute()
        )