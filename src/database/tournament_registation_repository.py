from database.connection import supabase

class TournamentRegistrationRepository:

    TABLE_FIELDS = (
        'id, tournament_id, team_id, registration_date, status'
    )

    @staticmethod
    def get_all():
        return(
            supabase
            .table('tournament_registrations')
            .select(TournamentRegistrationRepository.TABLE_FIELDS)
            .execute()
        )


    @staticmethod
    def get_by_registration_id(registration_id: int):
        return(
            supabase
            .table('tournament_registrations')
            .select(TournamentRegistrationRepository.TABLE_FIELDS)
            .eq('id', registration_id)
            .single()
            .execute()
        )


    @staticmethod
    def get_by_tournament_id(tournament_id: int):
        return(
            supabase
            .table('tournament_registrations')
            .select(TournamentRegistrationRepository.TABLE_FIELDS)
            .eq('id', tournament_id)
            .single()
            .execute()
        )


    @staticmethod
    def get_by_status(reg_status: str):
        return(
            supabase
            .table('tournament_registations')
            .select(TournamentRegistrationRepository.TABLE_FIELDS)
            .eq('status', reg_status)
            .single()
            .execute()
        )


    @staticmethod
    def create(data: dict):
        return(
            supabase
            .table('tournament_registrations')
            .insert(data)
            .execute()
        )


    @staticmethod
    def update_by_id(
            registration_id: int,
            status: str):

        return(
            supabase
            .table('tournament_registrations')
            .update({'status': status})
            .eq('id', registration_id)
        )


    @staticmethod
    def delete(reg_id: int):
        return(
            supabase
            .table('tournament_registrations')
            .delete()
            .eq('id', reg_id)
            .single()
            .execute()
        )