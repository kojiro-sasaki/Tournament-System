import pytest
from unittest.mock import MagicMock, patch

# 1. Import your actual Supabase client directly
# (If this gives an import error, remove "src." and use "from database.connection...")
from database.connection import supabase 

# 2. Import your repository
from database.repositories.tournament_repository import TournamentRepository

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
    
    with patch.object(supabase, 'table', side_effect=chain.table):
        yield chain

def test_get_all(mock_db):
    expected_response = {"data": [{"id": 1, "name": "Summer Cup"}]}
    mock_db.execute.return_value = expected_response

    result = TournamentRepository.get_all()

    assert result == expected_response
    mock_db.table.assert_called_with('tournaments')
    mock_db.select.assert_called_with(TournamentRepository.TOURNAMENT_FIELDS)
    mock_db.execute.assert_called_once()


def test_get_by_id(mock_db):
    expected_response = {"data": {"id": 5, "name": "Winter Brawl"}}
    mock_db.execute.return_value = expected_response

    result = TournamentRepository.get_by_id(5)

    assert result == expected_response
    mock_db.table.assert_called_with('tournaments')
    mock_db.eq.assert_called_with('id', 5)
    mock_db.single.assert_called_once()


def test_create(mock_db):
    new_data = {"name": "Spring Showdown", "game_id": 2}
    expected_response = {"data": [{"id": 10, **new_data}]}
    mock_db.execute.return_value = expected_response

    result = TournamentRepository.create(new_data)

    assert result == expected_response
    mock_db.insert.assert_called_with(new_data)


def test_update_by_id_filters_invalid_fields(mock_db):
    mock_db.execute.return_value = {"data": [{"id": 1}]}
    
    input_data = {
        "name": "Updated Name",
        "status": "ongoing",
        "hacker_field": "malicious_data"
    }

    result = TournamentRepository.update_by_id(1, input_data)

    assert result == {"data": [{"id": 1}]}
    
    expected_filtered_data = {
        "name": "Updated Name",
        "status": "ongoing"
    }
    mock_db.update.assert_called_with(expected_filtered_data)
    mock_db.eq.assert_called_with('id', 1)


def test_update_by_id_raises_value_error_on_empty_valid_fields():
    input_data = {"invalid_field": "data", "another_bad_field": 123}

    with pytest.raises(ValueError, match='No valid fields provided for update'):
        TournamentRepository.update_by_id(1, input_data)


def test_delete_by_id(mock_db):
    mock_db.execute.return_value = {"data": None}

    result = TournamentRepository.delete_by_id(10)

    mock_db.table.assert_called_with('tournaments')
    mock_db.delete.assert_called_once()
    mock_db.eq.assert_called_with('id', 10)
    mock_db.execute.assert_called_once()