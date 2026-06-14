import pytest
from unittest.mock import MagicMock, patch
from auth_backend.auth_service import register_user, RegistrationError

@pytest.fixture
def mock_supabase():
    with patch('database.connection.supabase') as mock:
        yield mock

@pytest.fixture
def mock_hash():
    with patch('auth_backend.auth_service.hash_password', return_value='fake_hash') as mock:
        yield mock

def test_register_user_success(mock_supabase, mock_hash):
    mock_response = MagicMock()
    mock_response.data = [{
        'id': '123',
        'username': 'captain_masha',
        'email': 'masha@example.com',
        'role': 'captain'
    }]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

    result = register_user('masha@example.com', 'captain_masha', 'password123')

    assert result['username'] == 'captain_masha'
    mock_hash.assert_called_once_with('password123')
    mock_supabase.table.assert_called_with('users')

def test_register_user_invalid_email(mock_supabase):
    with pytest.raises(RegistrationError, match="Invalid email format"):
        register_user('invalid-email', 'user1', 'password123')

def test_register_user_duplicate_email(mock_supabase, mock_hash):
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("duplicate key value for email")
    
    with pytest.raises(RegistrationError, match="Email already exists"):
        register_user('masha@example.com', 'captain_masha', 'password123')