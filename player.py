import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="Wattturnier", layout="centered")

# Mobile-friendly styling
st.markdown("""
    <style>
    .stButton > button { width: 100%; height: 50px; font-size: 18px; }
    .stSelectbox, .stNumberInput { font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

# Load data
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

tab1, tab2, tab3 = st.tabs(["📊 Tabelle", "🎯 Mein Tisch", "🍺 Speisekarte"])

with tab1:
    st.write("**Aktuelle Tabelle:**")
    
    if teams and matches:
        standings = []
        
        for team_num, team in enumerate(teams, start=1):
            name1 = f"{team['player1_last']} {team['player1_first'][0]}."
            name2 = f"{team['player2_last']} {team['player2_first'][0]}."
            team_name = f"{name1} - {name2}"
            
            wins = 0
            losses = 0
            points_for = 0
            points_against = 0
            
            for m in matches:
                if "scores" not in m:
                    continue
                    
                if m["team1"] == team_num:
                    for sub in m["scores"]:
                        points_for += sub[0]
                        points_against += sub[1]
                        if sub[0] == 15:
                            wins += 1
                        else:
                            losses += 1
                elif m["team2"] == team_num:
                    for sub in m["scores"]:
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
        st.table(df_standings.set_index("Platz"))
    else:
        st.write("Noch keine Daten vorhanden.")

with tab2:
    st.write("**Finde deinen Tisch:**")
    
    round_num = st.selectbox("Runde auswählen", [1, 2, 3])
    
    if teams:
        team_num = st.number_input("Deine Teamnummer", min_value=1, max_value=len(teams), step=1)
        
        if st.button("🔍 Tisch suchen"):
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
                st.info(f"Gegner: Team {opponent_num} — {opp_name}")
            else:
                st.warning("Keine Paarung für diese Runde gefunden.")
    else:
        st.write("Noch keine Teams registriert.")

with tab3:
    st.write("**Speisekarte:**")
    
    st.markdown("""
    ### 🍺 Getränke
    | Getränk | Preis |
    |---------|-------|
    | Bier, Weißbier, Radler | 3,50 € |
    | Alkoholfreie Getränke | 3,00 € |
    | Kurze | 2,50 € |
    | Rüscherl | 5,00 € |

    
    ### 🍕 Essen
    | Speise | Preis |
    |--------|-------|
    | Wurstsemmel | 3,00 € |
    | Pizzastück | 4,50 € |
    """)
    
    st.info("Bestellungen bitte an der Theke/Bedienung aufgeben!")