from services.login_service import LoginService
from auth_backend.password_utils import hash_password
class FakeRepository:

    def get_by_login(
        self,
        login
    ):
        if login == "team1":
            return {'password_hash': hash_password('123')}

        return None

def test_login_init():
    repo = FakeRepository()
    service = LoginService(repo)

    assert repo is service.account_repository

def test_login_success():

    service = LoginService(
        FakeRepository()
    )

    assert service.login(
        "team1",
        "123"
    )


def test_login_fail_wrong_password():

    service = LoginService(
        FakeRepository()
    )

    assert not service.login(
        "team1",
        "wrong"
    )

def test_login_fail_unknown_user():
    service = LoginService(FakeRepository())

    assert not service.login(
        "unknown",
        "123"
    )

def test_login_unknown_user_wrong_password():
    service = LoginService(FakeRepository())

    assert not service.login(
        "unknown",
        "123"
    )