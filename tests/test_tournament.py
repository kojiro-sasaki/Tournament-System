import pytest
from unittest.mock import MagicMock
from your_module import TournamentService

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def service(mock_repo):
    return TournamentService(mock_repo)

def test_create_tournament_success(service, mock_repo):
    mock_response = MagicMock()
    mock_response.data = [{"id": 1, "name": "Test Tournament"}]
    mock_repo.create.return_value = mock_response

    result = service.create_tournament(
        "Test Tournament", "Desc", 1, 8, "2026-06-01", "2026-06-10"
    )

    assert result["name"] == "Test Tournament"
    mock_repo.create.assert_called_once()
    args, _ = mock_repo.create.call_args
    assert args[0]["status"] == "Draft"

def test_create_tournament_missing_name(service):
    with pytest.raises(ValueError, match="Tournament name is required"):
        service.create_tournament("", "Desc", 1, 8, "2026-06-01", "2026-06-10")

def test_create_tournament_invalid_max_teams(service):
    with pytest.raises(ValueError, match="Max teams must be 8 or 16"):
        service.create_tournament("Name", "Desc", 1, 10, "2026-06-01", "2026-06-10")

@pytest.mark.parametrize("start_date, end_date", [
    ("01-06-2026", "2026-06-10"),
    ("2026-06-01", "2026/06/10"),
    ("bad-date", "2026-06-10")
])
def test_create_tournament_invalid_date_format(service, start_date, end_date):
    with pytest.raises(ValueError, match="Invalid date format. Use YYYY-MM-DD"):
        service.create_tournament("Name", "Desc", 1, 8, start_date, end_date)