from auth_backend.password_utils import verify_password

class LoginService:
    def __init__(self, account_repository):
        self.account_repository = account_repository

    def login(self, login: str, password: str) -> bool:
        if not login or not password:
            return False

        account = self.account_repository.get_by_login(login)

        if account is None:
            return False

        if not verify_password(password, account['password_hash']):
            return False

        return True
