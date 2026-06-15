import random
from typing import List, Dict


def generate_initial_bracket(tournament_id: int, teams: List[Dict], max_teams: int, start_match_id: int = 1) -> List[Dict]:
    if max_teams not in (8, 16):
        raise ValueError("max_teams must be 8 or 16")

    if len(teams) != max_teams:
        return []

    shuffled = teams.copy()
    random.shuffle(shuffled)

    matches = []
    num_matches = max_teams - 1
    first_round_matches = max_teams // 2
    first_round_name = "Round of 16" if max_teams == 16 else "Quarterfinals"

    for i in range(first_round_matches):
        t1 = shuffled[i * 2]
        t2 = shuffled[i * 2 + 1]
        matches.append({
            "id": start_match_id + i,
            "tournament_id": tournament_id,
            "round": first_round_name,
            "team1_id": t1["id"],
            "team1_name": t1["name"],
            "team2_id": t2["id"],
            "team2_name": t2["name"],
            "score1": 0,
            "score2": 0,
            "status": "Scheduled",
        })

    current_id = start_match_id + first_round_matches
    remaining_matches = num_matches - first_round_matches

    for i in range(remaining_matches):
        if remaining_matches - i == 1:
            round_name = "Finals"
        elif remaining_matches - i <= 3:
            round_name = "Semifinals"
        else:
            round_name = "Quarterfinals"

        matches.append({
            "id": current_id + i,
            "tournament_id": tournament_id,
            "round": round_name,
            "team1_id": None,
            "team1_name": "TBD",
            "team2_id": None,
            "team2_name": "TBD",
            "score1": 0,
            "score2": 0,
            "status": "Scheduled",
        })

    return matches
