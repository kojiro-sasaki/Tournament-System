import pytest
from unittest.mock import MagicMock, patch

from database.repositories.tournament_registration_repository import TournamentRegistrationRepository
import database.repositories.tournament_registration_repository as repo_module

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
    
    with patch.object(repo_module, 'supabase', chain):
        yield chain

def test_get_all(mock_db):
    expected_data = [{"id": 1, "tournament_id": 10, "team_id": 5, "status": "approved"}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TournamentRegistrationRepository.get_all()

    assert result.data == expected_data
    mock_db.table.assert_called_with('tournament_registrations')
    mock_db.select.assert_called_with(TournamentRegistrationRepository.TABLE_FIELDS)
    mock_db.execute.assert_called_once()

def test_get_by_registration_id(mock_db):
    expected_data = {"id": 1, "status": "pending"}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TournamentRegistrationRepository.get_by_registration_id(1)

    assert result.data == expected_data
    mock_db.table.assert_called_with('tournament_registrations')
    mock_db.eq.assert_called_with('id', 1)
    mock_db.single.assert_called_once()
    mock_db.execute.assert_called_once()

def test_get_by_team_id(mock_db):
    expected_data = [{"id": 1, "team_id": 5}, {"id": 2, "team_id": 5}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TournamentRegistrationRepository.get_by_team_id(5)

    assert result.data == expected_data
    mock_db.table.assert_called_with('tournament_registrations')
    mock_db.eq.assert_called_with('team_id', 5)
    mock_db.execute.assert_called_once()

def test_get_by_tournament_id(mock_db):
    expected_data = {"id": 10, "tournament_id": 10}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TournamentRegistrationRepository.get_by_tournament_id(10)

    assert result.data == expected_data
    mock_db.table.assert_called_with('tournament_registrations')
    mock_db.eq.assert_called_with('id', 10)
    mock_db.single.assert_called_once()
    mock_db.execute.assert_called_once()

def test_get_by_status(mock_db):
    expected_data = {"id": 3, "status": "approved"}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TournamentRegistrationRepository.get_by_status("approved")

    assert result.data == expected_data
    mock_db.table.assert_called_with('tournament_registrations')
    mock_db.eq.assert_called_with('status', "approved")
    mock_db.single.assert_called_once()
    mock_db.execute.assert_called_once()

def test_create(mock_db):
    new_data = {"tournament_id": 1, "team_id": 2, "status": "pending"}
    expected_data = [{"id": 5, **new_data}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TournamentRegistrationRepository.create(new_data)

    assert result.data == expected_data
    mock_db.table.assert_called_with('tournament_registrations')
    mock_db.insert.assert_called_with(new_data)
    mock_db.execute.assert_called_once()

def test_update_by_id_filters_invalid_fields(mock_db):
    mock_response = MagicMock()
    mock_response.data = [{"id": 1, "status": "approved"}]
    mock_db.execute.return_value = mock_response
    
    input_data = {
        "status": "approved",
        "tournament_id": 99,
        "team_id": 123 
    }

    result = TournamentRegistrationRepository.update_by_id(1, input_data)

    assert result.data == [{"id": 1, "status": "approved"}]
    
    expected_filtered_data = {
        "status": "approved"
    }
    mock_db.update.assert_called_with(expected_filtered_data)
    mock_db.eq.assert_called_with('id', 1)
    mock_db.execute.assert_called_once()

def test_update_by_id_raises_value_error_on_empty_valid_fields():
    input_data = {"tournament_id": 99, "hacker_field": "test"}

    with pytest.raises(ValueError, match="No valid fields frovided for update"):
        TournamentRegistrationRepository.update_by_id(1, input_data)

def test_delete(mock_db):
    mock_response = MagicMock()
    mock_response.data = None
    mock_db.execute.return_value = mock_response

    result = TournamentRegistrationRepository.delete(42)

    mock_db.table.assert_called_with('tournament_registrations')
    mock_db.delete.assert_called_once()
    mock_db.eq.assert_called_with('id', 42)
    mock_db.execute.assert_called_once()