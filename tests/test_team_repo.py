import pytest
from unittest.mock import MagicMock, patch

from database.repositories.team_repository import TeamRepository
import database.repositories.team_repository as repo_module

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
    expected_data = [{"id": 1, "name": "Team Liquid", "tag": "TL", "captain_id": 5}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TeamRepository.get_all()

    assert result.data == expected_data
    mock_db.table.assert_called_with('teams')
    mock_db.select.assert_called_with(TeamRepository.TEAM_FIELDS)
    mock_db.execute.assert_called_once()


def test_get_by_id(mock_db):
    expected_data = {"id": 10, "name": "Cloud9", "tag": "C9"}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TeamRepository.get_by_id(10)

    assert result.data == expected_data
    mock_db.table.assert_called_with('teams')
    mock_db.eq.assert_called_with('id', 10)
    mock_db.single.assert_called_once()
    mock_db.execute.assert_called_once()


def test_get_by_name(mock_db):
    expected_data = {"id": 4, "name": "Fnatic", "tag": "FNC"}
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TeamRepository.get_by_name("Fnatic")

    assert result.data == expected_data
    mock_db.table.assert_called_with('teams')
    mock_db.eq.assert_called_with('name', "Fnatic")
    mock_db.single.assert_called_once()
    mock_db.execute.assert_called_once()


def test_get_by_captain_id(mock_db):
    expected_data = [{"id": 1, "captain_id": 99}, {"id": 2, "captain_id": 99}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TeamRepository.get_by_captain_id(99)

    assert result.data == expected_data
    mock_db.table.assert_called_with('teams')
    mock_db.eq.assert_called_with('captain_id', 99)
    mock_db.execute.assert_called_once()


def test_create(mock_db):
    new_team_data = {"name": "G2 Esports", "tag": "G2", "captain_id": 7}
    expected_data = [{"id": 8, **new_team_data}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = TeamRepository.create(new_team_data)

    assert result.data == expected_data
    mock_db.table.assert_called_with('teams')
    mock_db.insert.assert_called_with(new_team_data)
    mock_db.execute.assert_called_once()


def test_update_by_id_filters_invalid_fields(mock_db):
    mock_response = MagicMock()
    mock_response.data = [{"id": 1, "name": "New Name"}]
    mock_db.execute.return_value = mock_response
    
    input_data = {
        "name": "New Name",
        "tag": "NN",
        "created_at": "2023-01-01",
        "wins": 50
    }

    result = TeamRepository.update_by_id(1, input_data)

    assert result.data == [{"id": 1, "name": "New Name"}]
    
    expected_filtered_data = {
        "name": "New Name",
        "tag": "NN"
    }
    mock_db.update.assert_called_with(expected_filtered_data)
    mock_db.eq.assert_called_with('id', 1)
    mock_db.execute.assert_called_once()


def test_update_by_id_raises_value_error_on_empty_valid_fields():
    input_data = {"is_banned": False, "points": 100}

    with pytest.raises(ValueError, match="No valid fields provided for update"):
        TeamRepository.update_by_id(1, input_data)


def test_delete_by_id(mock_db):
    mock_response = MagicMock()
    mock_response.data = None
    mock_db.execute.return_value = mock_response

    result = TeamRepository.delete_by_id(42)

    mock_db.table.assert_called_with('teams')
    mock_db.delete.assert_called_once()
    mock_db.eq.assert_called_with('id', 42)
    mock_db.execute.assert_called_once()