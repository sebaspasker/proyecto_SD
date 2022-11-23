def search_players_dict(char, players_dict):
    for key in players_dict.keys():
        if key[0].lower() == char:
            return players_dict[key]
    return None
