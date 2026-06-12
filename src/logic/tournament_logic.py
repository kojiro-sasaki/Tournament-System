def generate_matches(tournament_id, selected_teams, max_teams, start_match_id=1):
    matches = []
    if max_teams not in (8, 16):
        return matches

    num_matches = max_teams - 1
    first_round_matches = max_teams // 2
    first_round_name = "Round of 16" if max_teams == 16 else "Quarterfinals"
    
    for i in range(first_round_matches):
        matches.append({
            "id": start_match_id + i,
            "tournament_id": tournament_id,
            "round": first_round_name,
            "time": "TBD",
            "team1": selected_teams[i*2] if i*2 < len(selected_teams) else "TBD",
            "score1": 0,
            "team2": selected_teams[i*2+1] if i*2+1 < len(selected_teams) else "TBD",
            "score2": 0,
            "status": "Scheduled"
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
            "time": "TBD",
            "team1": "TBD",
            "score1": 0,
            "team2": "TBD",
            "score2": 0,
            "status": "Scheduled"
        })
        
    return matches

def get_next_match_index(current_index, total_matches):
    return (current_index // 2) + (total_matches + 1) // 2
