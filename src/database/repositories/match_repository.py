from database.connection import supabase

class MatchRepository:

    MATCH_FIELDS = (
        'id, tournament_id, team1_id, team2_id, match_date, status, round_name'
    )


    @staticmethod
    def get_all():
        return(
            supabase
            .table('matches')
            .select(MatchRepository.MATCH_FIELDS)
            .execute()
        )


    @staticmethod
    def get_by_id(match_id: int):
        return(
            supabase
            .table('matches')
            .select(MatchRepository.MATCH_FIELDS)
            .eq('id', match_id)
            .single()
            .execute()
        )


    @staticmethod
    def get_by_tournament_id(tournament_id: int):
        return(
            supabase
            .table('matches')
            .select(MatchRepository.MATCH_FIELDS)
            .eq('tournament_id', tournament_id)
            .execute()
        )


    @staticmethod
    def get_by_status(status: str):
        return(
            supabase
            .table('matches')
            .select(MatchRepository.MATCH_FIELDS)
            .eq('status', status)
            .execute()
        )


    @staticmethod
    def create(data: dict):
        return(
            supabase
            .table('matches')
            .insert(data)
            .execute()
        )


    @staticmethod
    def update_by_id(
            match_id: int,
            data: dict
    ):

        allowed_fields = {
            'team1_id',
            'team2_id',
            'match_date',
            'status',
            'round_name'
        }

        filtered_data = {
            key: value
            for key, value in data.items()
            if key in allowed_fields
        }

        if not filtered_data:
            raise ValueError(
                "No valid fields provided for update"
            )

        return(
            supabase
            .table('matches')
            .update(filtered_data)
            .eq('id', match_id)
            .execute()
        )

    @staticmethod
    def update_by_tournament_id(
            tournament_id: int,
            data: dict
    ):

        allowed_fields = {
            'match_date',
            'status',
            'round_name'
        }

        filtered_data = {
            key: value
            for key, value in data.items()
            if key in allowed_fields
        }

        if not filtered_data:
            raise ValueError(
                "No valid fields provided for update"
            )

        return (
            supabase
            .table('matches')
            .update(filtered_data)
            .eq('id', tournament_id)
            .execute()
        )



    @staticmethod
    def delete_by_id(match_id: int):
        return(
            supabase
            .table('matches')
            .delete()
            .eq('id', match_id)
            .execute()
        )