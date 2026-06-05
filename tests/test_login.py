from src.services.login_service import LoginService


class FakeRepository:

    def get_by_login(
        self,
        login
    ):

        class Account:

            password = "123"

        if login == "team1":
            return Account()

        return None


def test_login_success():

    service = LoginService(
        FakeRepository()
    )

    assert service.login(
        "team1",
        "123"
    )


def test_login_fail():

    service = LoginService(
        FakeRepository()
    )

    assert not service.login(
        "team1",
        "wrong"
    )