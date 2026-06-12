from database.connection import supabase

class GameRepository:

    GAME_FIELDS = (
        'id',
        'name'
    )


    @staticmethod
    def get_all():

        return(
            supabase
            .table('games')
            .select(GameRepository.GAME_FIELDS)
            .execute()
        )


    @staticmethod
    def get_by_id(game_id: int):

        return(
            supabase
            .table('games')
            .select(GameRepository.GAME_FIELDS)
            .eq('id', game_id)
            .execute()
        )


    @staticmethod
    def get_by_name(name: str):

        return (
            supabase
            .table('games')
            .select(GameRepository.GAME_FIELDS)
            .eq('name', name)
            .execute()
        )


    @staticmethod
    def create(data: dict):

        return(
            supabase
            .table('games')
            .insert(data)
            .execute()
        )


    @staticmethod
    def update_by_id(
            game_id: int,
            data: dict
    ):

        allowed_fields = {
            'name'
        }

        filtered_data = {
            key: value
            for key, value in data.items()
            if key in allowed_fields
        }

        if not filtered_data:
            raise ValueError(
                "No allowed fields provided in data"
            )

        return(
            supabase
            .table('games')
            .update(filtered_data)
            .eq('id', game_id)
            .execute()
        )


    @staticmethod
    def delete_by_id(game_id: int):

        return(
            supabase
            .table('games')
            .delete()
            .eq('id', game_id)
            .execute()
        )