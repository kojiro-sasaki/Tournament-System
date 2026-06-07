from database.connection import supabase

class AccountRepository:
    def get_by_login(self, login: str):
        try:
            response = supabase.table('users') \
                .select('*') \
                .eq('username', login) \
                .single() \
                .execute()
            return response.data
        except Exception:
            return None
