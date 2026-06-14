import pytest
from unittest.mock import MagicMock, patch

from database.repositories.match_repository import MatchRepository
import database.repositories.match_repository as repo_module

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
    expected_data = [{"id": 1, "tournament_id": 10, "status": "scheduled"}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = MatchRepository.get_all()

    assert result.data == expected_data
    mock_db.table.assert_called_with('matches')
    mock_db.select.assert_called_with(MatchRepository.MATCH_FIELDS)
    mock_db.execute.assert_called_once()


def test_get_by_id(mock_db):
    expected_data = {"id": 5, "team1_id": 2, "team2_id": 3}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = MatchRepository.get_by_id(5)

    assert result.data == expected_data
    mock_db.table.assert_called_with('matches')
    mock_db.eq.assert_called_with('id', 5)
    mock_db.single.assert_called_once()
    mock_db.execute.assert_called_once()


def test_get_by_tournament_id(mock_db):
    expected_data = [{"id": 1, "tournament_id": 10}, {"id": 2, "tournament_id": 10}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = MatchRepository.get_by_tournament_id(10)

    assert result.data == expected_data
    mock_db.table.assert_called_with('matches')
    mock_db.eq.assert_called_with('tournament_id', 10)
    mock_db.execute.assert_called_once()


def test_get_by_status(mock_db):
    expected_data = [{"id": 1, "status": "completed"}, {"id": 4, "status": "completed"}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = MatchRepository.get_by_status("completed")

    assert result.data == expected_data
    mock_db.table.assert_called_with('matches')
    mock_db.eq.assert_called_with('status', "completed")
    mock_db.execute.assert_called_once()


def test_create(mock_db):
    new_match_data = {"tournament_id": 1, "team1_id": 2, "team2_id": 3, "round_name": "Finals"}
    expected_data = [{"id": 99, **new_match_data}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = MatchRepository.create(new_match_data)

    assert result.data == expected_data
    mock_db.table.assert_called_with('matches')
    mock_db.insert.assert_called_with(new_match_data)
    mock_db.execute.assert_called_once()


def test_update_by_id_filters_invalid_fields(mock_db):
    mock_response = MagicMock()
    mock_response.data = [{"id": 1, "status": "ongoing"}]
    mock_db.execute.return_value = mock_response
    
    input_data = {
        "status": "ongoing",
        "round_name": "Semi-Finals",
        "tournament_id": 50
    }

    result = MatchRepository.update_by_id(1, input_data)

    assert result.data == [{"id": 1, "status": "ongoing"}]
    
    expected_filtered_data = {
        "status": "ongoing",
        "round_name": "Semi-Finals"
    }
    mock_db.update.assert_called_with(expected_filtered_data)
    mock_db.eq.assert_called_with('id', 1)
    mock_db.execute.assert_called_once()


def test_update_by_id_raises_value_error_on_empty_valid_fields():
    input_data = {"tournament_id": 50, "winner_id": 2}

    with pytest.raises(ValueError, match="No valid fields provided for update"):
        MatchRepository.update_by_id(1, input_data)


def test_update_by_tournament_id_filters_invalid_fields(mock_db):
    mock_response = MagicMock()
    mock_response.data = [{"id": 1, "status": "delayed"}]
    mock_db.execute.return_value = mock_response
    
    input_data = {
        "status": "delayed",
        "team1_id": 5
    }

    result = MatchRepository.update_by_tournament_id(10, input_data)

    assert result.data == [{"id": 1, "status": "delayed"}]
    
    expected_filtered_data = {
        "status": "delayed"
    }
    mock_db.update.assert_called_with(expected_filtered_data)
    
    mock_db.eq.assert_called_with('id', 10)
    mock_db.execute.assert_called_once()


def test_update_by_tournament_id_raises_value_error():
    input_data = {"team1_id": 5, "team2_id": 6}

    with pytest.raises(ValueError, match="No valid fields provided for update"):
        MatchRepository.update_by_tournament_id(10, input_data)


def test_delete_by_id(mock_db):
    mock_response = MagicMock()
    mock_response.data = None
    mock_db.execute.return_value = mock_response

    result = MatchRepository.delete_by_id(42)

    mock_db.table.assert_called_with('matches')
    mock_db.delete.assert_called_once()
    mock_db.eq.assert_called_with('id', 42)
    mock_db.execute.assert_called_once()