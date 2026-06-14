from database.connection import supabase

class TeamRepository:


    TEAM_FIELDS = (
        'id, name,tag, captain_id, created_at,description,tournament_wins'
    )

    @staticmethod
    def get_all():
        return(
            supabase
            .table('teams')
            .select(TeamRepository.TEAM_FIELDS)
            .execute()
        )


    @staticmethod
    def get_by_id(team_id: int):
        return(
            supabase
            .table('teams')
            .select(TeamRepository.TEAM_FIELDS)
            .eq('id', team_id)
            .single()
            .execute()
        )


    @staticmethod
    def get_by_name(name: str):
        return(
            supabase
            .table('teams')
            .select(TeamRepository.TEAM_FIELDS)
            .eq('name', name)
            .single()
            .execute()
        )


    @staticmethod
    def get_by_captain_id(captain_id: int):
        return(
            supabase
            .table('teams')
            .select(TeamRepository.TEAM_FIELDS)
            .eq('captain_id', captain_id)
            .execute()
        )


    @staticmethod
    def create(data: dict):
        return(
            supabase
            .table('teams')
            .insert(data)
            .execute()
        )


    @staticmethod
    def update_by_id(
            team_id: int,
            data: dict
    ):

        allowed_fields = (
            'name',
            'captain_id',
            'description',
            'tag',
            'tournament_wins'
        )

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
            .table('teams')
            .update(filtered_data)
            .eq('id', team_id)
            .execute()
        )


    @staticmethod
    def delete_by_id(team_id: int):
        return(
            supabase
            .table('teams')
            .delete()
            .eq('id', team_id)
            .execute()
        )

