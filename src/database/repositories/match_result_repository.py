from database.connection import supabase
class MatchResultRepository:

    @staticmethod
    def get_by_match_id(match_id: int):
        return (
            supabase
            .table("match_results")
            .select("*")
            .eq("match_id", match_id)
            .single()
            .execute()
        )

    @staticmethod
    def create(data: dict):
        return (
            supabase
            .table("match_results")
            .insert(data)
            .execute()
        )

    @staticmethod
    def get_all():
        return (
            supabase
            .table("match_results")
            .select("*")
            .execute()
        )