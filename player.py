import streamlit as st
import json
import pandas as pd

# Load data (read-only)
try:
    with open("teams.json", "r") as f:
        teams = json.load(f)
except FileNotFoundError:
    teams = []

try:
    with open("matches.json", "r") as f:
        matches = json.load(f)
except FileNotFoundError:
    matches = []

st.title("🃏 Wattturnier SV Wörth 2025")

tab1, tab2 = st.tabs(["Tabelle", "Mein Tisch"])

with tab1:
    st.write("Aktuelle Tabelle:")
    
    if teams and matches:
        standings = []
        
        for team_num, team in enumerate(teams, start=1):
            name1 = f"{team['player1_last']} {team['player1_first'][0]}."
            name2 = f"{team['player2_last']} {team['player2_first'][0]}."
            team_name = f"{name1} - {name2}"
            
            games_played = 0
            wins = 0
            losses = 0
            points_for = 0
            points_against = 0
            
            for m in matches:
                if "scores" not in m:
                    continue
                    
                if m["team1"] == team_num:
                    for sub in m["scores"]:
                        games_played += 1
                        points_for += sub[0]
                        points_against += sub[1]
                        if sub[0] == 15:
                            wins += 1
                        else:
                            losses += 1
                elif m["team2"] == team_num:
                    for sub in m["scores"]:
                        games_played += 1
                        points_for += sub[1]
                        points_against += sub[0]
                        if sub[1] == 15:
                            wins += 1
                        else:
                            losses += 1
            
            standings.append({
                "Platz": 0,
                "Team": team_num,
                "Name": team_name,
                "Spiele": f"{wins}:{losses}",
                "Punkte": f"{points_for}:{points_against}",
                "wins": wins,
                "pf": points_for,
                "pa": points_against
            })
        
        standings.sort(key=lambda x: (-x["wins"], -x["pf"], x["pa"]))
        
        for i, s in enumerate(standings):
            s["Platz"] = i + 1
        
        df_standings = pd.DataFrame(standings)[["Platz", "Team", "Name", "Spiele", "Punkte"]]
        st.dataframe(df_standings, hide_index=True)
    else:
        st.write("Noch keine Daten vorhanden.")

with tab2:
    st.write("Finde deinen Tisch:")
    
    round_num = st.selectbox("Runde auswählen", [1, 2, 3])
    team_num = st.number_input("Deine Teamnummer", min_value=1, max_value=len(teams) if teams else 1, step=1)
    
    if st.button("Tisch suchen"):
        round_matches = [m for m in matches if m["round"] == round_num]
        
        my_match = None
        for m in round_matches:
            if m["team1"] == team_num or m["team2"] == team_num:
                my_match = m
                break
        
        if my_match:
            opponent_num = my_match["team2"] if my_match["team1"] == team_num else my_match["team1"]
            opponent = teams[opponent_num - 1]
            opp_name = f"{opponent['player1_last']} {opponent['player1_first'][0]}. - {opponent['player2_last']} {opponent['player2_first'][0]}."
            
            st.success(f"🎯 Tisch {my_match['table']}")
            st.write(f"Gegner: Team {opponent_num} — {opp_name}")
        else:
            st.warning("Keine Paarung für diese Runde gefunden.")