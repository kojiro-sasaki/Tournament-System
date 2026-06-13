import pytest
from logic.tournament_logic import generate_matches, get_next_match_index

def test_generate_matches_8_teams():
    teams = ["Team A", "Team B", "Team C", "Team D", "Team E", "Team F", "Team G", "Team H"]
    matches = generate_matches("tourn_1", teams, 8)
    
    assert len(matches) == 7
    
    assert matches[0]["round"] == "Quarterfinals"
    assert matches[0]["team1"] == "Team A"
    assert matches[0]["team2"] == "Team B"
    
    assert matches[-1]["round"] == "Finals"
    assert matches[-1]["team1"] == "TBD"

def test_generate_matches_invalid_teams():
    assert generate_matches("tourn_1", [], 10) == []

def test_get_next_match_index():
    assert get_next_match_index(1, 7) == 4