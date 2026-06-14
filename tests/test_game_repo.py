import pytest
from unittest.mock import MagicMock, patch

from database.repositories.game_repository import GameRepository
import database.repositories.game_repository as repo_module

@pytest.fixture
def mock_db():
    chain = MagicMock()
    
    chain.table.return_value = chain
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.insert.return_value = chain
    chain.update.return_value = chain
    chain.delete.return_value = chain
    
    with patch.object(repo_module, 'supabase', chain):
        yield chain

def test_get_all(mock_db):
    expected_data = [{"id": 1, "name": "League of Legends"}, {"id": 2, "name": "Valorant"}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = GameRepository.get_all()

    assert result.data == expected_data
    mock_db.table.assert_called_with('games')
    mock_db.select.assert_called_with(GameRepository.GAME_FIELDS)
    mock_db.execute.assert_called_once()


def test_get_by_id(mock_db):
    expected_data = [{"id": 5, "name": "Counter-Strike 2"}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = GameRepository.get_by_id(5)

    assert result.data == expected_data
    mock_db.table.assert_called_with('games')
    mock_db.select.assert_called_with(GameRepository.GAME_FIELDS)
    mock_db.eq.assert_called_with('id', 5)
    mock_db.execute.assert_called_once()


def test_get_by_name(mock_db):
    expected_data = [{"id": 3, "name": "Dota 2"}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = GameRepository.get_by_name("Dota 2")

    assert result.data == expected_data
    mock_db.table.assert_called_with('games')
    mock_db.select.assert_called_with(GameRepository.GAME_FIELDS)
    mock_db.eq.assert_called_with('name', "Dota 2")
    mock_db.execute.assert_called_once()


def test_create(mock_db):
    new_game_data = {"name": "Overwatch 2"}
    expected_data = [{"id": 10, "name": "Overwatch 2"}]
    mock_response = MagicMock()
    mock_response.data = expected_data
    mock_db.execute.return_value = mock_response

    result = GameRepository.create(new_game_data)

    assert result.data == expected_data
    mock_db.table.assert_called_with('games')
    mock_db.insert.assert_called_with(new_game_data)
    mock_db.execute.assert_called_once()


def test_update_by_id_filters_invalid_fields(mock_db):
    mock_response = MagicMock()
    mock_response.data = [{"id": 1, "name": "Rocket League"}]
    mock_db.execute.return_value = mock_response
    
    input_data = {
        "name": "Rocket League",
        "developer": "Psyonix",
        "release_year": 2015   
    }

    result = GameRepository.update_by_id(1, input_data)

    assert result.data == [{"id": 1, "name": "Rocket League"}]
    
    expected_filtered_data = {
        "name": "Rocket League"
    }
    mock_db.update.assert_called_with(expected_filtered_data)
    mock_db.eq.assert_called_with('id', 1)
    mock_db.execute.assert_called_once()


def test_update_by_id_raises_value_error_on_empty_valid_fields():
    input_data = {"developer": "Valve", "genre": "MOBA"}

    with pytest.raises(ValueError, match="No allowed fields provided in data"):
        GameRepository.update_by_id(3, input_data)


def test_delete_by_id(mock_db):
    mock_response = MagicMock()
    mock_response.data = None
    mock_db.execute.return_value = mock_response

    result = GameRepository.delete_by_id(7)

    mock_db.table.assert_called_with('games')
    mock_db.delete.assert_called_once()
    mock_db.eq.assert_called_with('id', 7)
    mock_db.execute.assert_called_once()