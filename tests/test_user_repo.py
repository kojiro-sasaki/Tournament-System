import pytest
from unittest.mock import MagicMock, patch

from database.repositories.user_repository import UserRepository
import database.repositories.user_repository as user_repo_module

@pytest.fixture
def mock_db():
    chain = MagicMock()
    
    chain.table.return_value = chain
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.single.return_value = chain
    chain.insert.return_value = chain
    chain.update.return_value = chain
    chain.delete.return_value = chain
    
    with patch.object(user_repo_module, 'supabase', chain):
        yield chain


def test_get_auth_data_by_login(mock_db):
    expected_data = {"id": 1, "username": "admin", "password_hash": "hashed123", "role": "admin"}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = UserRepository.get_auth_data_by_login("admin")

    assert result.data == expected_data
    mock_db.table.assert_called_with('users')
    mock_db.select.assert_called_with('id, username, password_hash, role')
    mock_db.eq.assert_called_with('username', "admin")
    mock_db.single.assert_called_once()
    mock_db.execute.assert_called_once()


def test_get_all(mock_db):
    expected_data = [
        {"id": 1, "username": "player1", "email": "p1@test.com"},
        {"id": 2, "username": "player2", "email": "p2@test.com"}
    ]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = UserRepository.get_all()

    assert result.data == expected_data
    mock_db.table.assert_called_with('users')
    mock_db.select.assert_called_with(UserRepository.USER_FIELDS)
    mock_db.execute.assert_called_once()


def test_get_by_id(mock_db):
    expected_data = {"id": 10, "username": "player10"}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = UserRepository.get_by_id(10)

    assert result.data == expected_data
    mock_db.table.assert_called_with('users')
    mock_db.select.assert_called_with(UserRepository.USER_FIELDS)
    mock_db.eq.assert_called_with('id', 10)
    mock_db.single.assert_called_once()


def test_get_by_username(mock_db):
    expected_data = {"id": 5, "username": "pro_gamer"}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = UserRepository.get_by_username("pro_gamer")

    assert result.data == expected_data
    mock_db.eq.assert_called_with('username', "pro_gamer")
    mock_db.single.assert_called_once()


def test_get_by_email(mock_db):
    expected_data = {"id": 2, "email": "hello@world.com"}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = UserRepository.get_by_email("hello@world.com")

    assert result.data == expected_data
    mock_db.eq.assert_called_with('email', "hello@world.com")
    mock_db.single.assert_called_once()


def test_create(mock_db):
    expected_data = [{"id": 7, "username": "newbie", "email": "new@test.com"}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = UserRepository.create("newbie", "new@test.com", "supersecret")

    assert result.data == expected_data
    mock_db.table.assert_called_with('users')
    mock_db.insert.assert_called_with({
        'username': "newbie",
        'email': "new@test.com",
        'password_hash': "supersecret"
    })
    mock_db.execute.assert_called_once()


def test_update_by_id_filters_invalid_fields(mock_db):
    mock_response = MagicMock()
    mock_response.data = [{"id": 1}]
    mock_db.execute.return_value = mock_response
    
    input_data = {
        "username": "updated_user",
        "role": "admin",
        "is_banned": True,
        "login_count": 5 
    }

    result = UserRepository.update_by_id(1, input_data)

    assert result.data == [{"id": 1}]
    
    expected_filtered_data = {
        "username": "updated_user",
        "role": "admin"
    }
    mock_db.update.assert_called_with(expected_filtered_data)
    mock_db.eq.assert_called_with('id', 1)


def test_update_by_id_raises_value_error_on_empty_valid_fields():
    input_data = {"is_banned": True, "favorite_color": "blue"}

    with pytest.raises(ValueError, match="No valid fields provided for update"):
        UserRepository.update_by_id(1, input_data)


def test_delete_by_id(mock_db):
    mock_response = MagicMock()
    mock_response.data = None
    mock_db.execute.return_value = mock_response

    result = UserRepository.delete_by_id(99)

    mock_db.table.assert_called_with('users')
    mock_db.delete.assert_called_once()
    mock_db.eq.assert_called_with('id', 99)
    mock_db.execute.assert_called_once()