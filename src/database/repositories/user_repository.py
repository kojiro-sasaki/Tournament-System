
from database.connection import supabase

class UserRepository:

    USER_FIELDS = (
        'id, username, email, role, created_at'
    )

    @staticmethod
    def get_auth_data_by_login(login: str):
        return(
            supabase
            .table('users')
            .select('id, username, password_hash, role')
            .eq('username', login)
            .single()
            .execute()
        )


    @staticmethod
    def get_all():
        return (
            supabase
            .table('users')
            .select(UserRepository.USER_FIELDS)
            .execute()
        )


    @staticmethod
    def get_by_id(user_id):
        return(
            supabase
            .table('users')
            .select(UserRepository.USER_FIELDS)
            .eq('id', user_id)
            .single()
            .execute()
        )


    @staticmethod
    def get_by_username(username):
        return (
            supabase
            .table('users')
            .select(UserRepository.USER_FIELDS)
            .eq('username', username)
            .single()
            .execute()
        )


    @staticmethod
    def get_by_email(email):
        return (
            supabase
            .table('users')
            .select(UserRepository.USER_FIELDS)
            .eq('email', email)
            .single()
            .execute()
        )


    @staticmethod
    def create(
            username: str,
            email: str,
            password_hash: str
    ):
        return(
            supabase
            .table('users')
            .insert({
                'username': username,
                'email': email,
                'password_hash': password_hash
            })
            .execute()
        )


    @staticmethod
    def update_by_id(
        user_id: int,
        data: dict
    ):
        allowed_fields = {
            'username',
            'email',
            'password_hash',
            'role'
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
            .table('users')
            .update(filtered_data)
            .eq('id', user_id)
            .execute()
        )


    @staticmethod
    def delete_by_id(user_id: int):
        return(
            supabase
            .table('users')
            .delete()
            .eq('id', user_id)
            .execute()
        )
