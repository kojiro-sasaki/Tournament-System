class LoginService:

    def __init__(self, account_repository):

        self.account_repository = account_repository

    def login(
        self,
        login: str,
        password: str
    ) -> bool:

        account = self.account_repository.get_by_login(
            login
        )

        if account is None:
            return False

        if account.password != password:
            return False

        return True