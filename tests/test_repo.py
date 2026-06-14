import pytest
from unittest.mock import MagicMock, patch

from database.repositories.repository import AccountRepository
import database.repositories.repository as repo_module

@pytest.fixture
def mock_db():
    chain = MagicMock()
    
    chain.table.return_value = chain
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.single.return_value = chain
    chain.execute.return_value = chain
    
    with patch.object(repo_module, 'supabase', chain):
        yield chain

def test_get_by_login_success(mock_db):
    expected_data = {"id": 1, "username": "admin", "role": "superuser"}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    repo = AccountRepository()
    result = repo.get_by_login("admin")

    assert result == expected_data
    mock_db.table.assert_called_with('users')
    mock_db.select.assert_called_with('*')
    mock_db.eq.assert_called_with('username', "admin")
    mock_db.single.assert_called_once()
    mock_db.execute.assert_called_once()


def test_get_by_login_handles_exception_and_returns_none(mock_db):
    mock_db.execute.side_effect = Exception("Something went wrong in the database")

    repo = AccountRepository()
    result = repo.get_by_login("non_existent_user")

    assert result is None
    
    mock_db.table.assert_called_with('users')
    mock_db.eq.assert_called_with('username', "non_existent_user")