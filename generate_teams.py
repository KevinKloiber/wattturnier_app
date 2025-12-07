import json

teams = []
for i in range(1, 61):
    teams.append({
        "player1_first": f"Spieler{i}A",
        "player1_last": f"Nachname{i}A",
        "player2_first": f"Spieler{i}B",
        "player2_last": f"Nachname{i}B"
    })

with open("teams.json", "w") as f:
    json.dump(teams, f)
