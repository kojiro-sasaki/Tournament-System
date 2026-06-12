from datetime import datetime
from database.connection import supabase

class TournamentRepository:
    def create(self, name, description, game_id, max_teams, start_date, end_date, status):
        response = supabase.table('tournaments').insert({
            'name': name,
            'description': description,
            'game_id': game_id,
            'max_teams': max_teams,
            'start_date': start_date,
            'end_date': end_date,
            'status': status,
        }).execute()

        if response.data:
            return response.data[0]
        return None

    def get_all(self):
        response = supabase.table('tournaments').select('*').execute()
        return response.data or []

    def delete(self, tournament_id):
        supabase.table('tournaments').delete().eq('id', tournament_id).execute()

    def update_status(self, tournament_id, new_status):
        supabase.table('tournaments').update(
            {'status': new_status}
        ).eq('id', tournament_id).execute()