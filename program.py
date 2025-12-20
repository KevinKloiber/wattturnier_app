import streamlit as st
import json
import os
import pandas as pd
import random

if "teams" not in st.session_state:
    try:
        with open("teams.json", "r") as f:
            st.session_state.teams = json.load(f)
    except FileNotFoundError:
        st.session_state.teams = []

if "matches" not in st.session_state:
    try:
        with open("matches.json", "r") as f:
            st.session_state.matches = json.load(f)
    except FileNotFoundError:
        st.session_state.matches = []



st.title("Wattturnier SV Wörth 2025")


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Registrierung", "Angemeldete Teams", "Partienplan", "Ergebnisse eintragen", "Tabelle"])


with tab1:
    fn1 = st.text_input("Vorname 1", "")
    ln1 = st.text_input("Nachname 1", "")

    fn2 = st.text_input("Vorname 2", "")
    ln2 = st.text_input("Nachname 2", "")

    if st.button("Teilnehmer registrieren"):
        team = {"player1_first": fn1, "player1_last": ln1, "player2_first": fn2, "player2_last": ln2}
        st.session_state.teams.append(team)
        st.write("Teilnehmer registriert. Team Nummer:", len(st.session_state.teams))
        with open("teams.json", "w") as f:
            json.dump(st.session_state.teams, f)

    st.divider()
    st.write("⚠️ Gefahrenzone:")
    delete_confirm = st.text_input("Zum Löschen 'DELETE' eingeben:", key="delete_confirm")
    if st.button("Alle Daten löschen"):
        if delete_confirm == "DELETE":
            st.session_state.teams = []
            st.session_state.matches = []
            with open("teams.json", "w") as f:
                json.dump([], f)
            with open("matches.json", "w") as f:
                json.dump([], f)
            st.success("Alle Daten gelöscht!")
        else:
            st.error("Bitte 'DELETE' eingeben zum Bestätigen.")

with tab2: 
    st.write("Angemeldete Teams:")
    
    if st.session_state.teams:
        df = pd.DataFrame(st.session_state.teams)
        df.index += 1
        df.columns = ["Vorname 1", "Nachname 1", "Vorname 2", "Nachname 2"]
        edited_df = st.data_editor(df)
        edited_df.columns = ["player1_first", "player1_last", "player2_first", "player2_last"]

        if st.button("Aktualisieren"):
            st.session_state.teams = edited_df.to_dict(orient="records")
            with open("teams.json", "w") as f:
                json.dump(st.session_state.teams, f)
            st.write("Teilnehmerliste aktualisiert.")
    else:
        st.write("Noch keine Teams registriert.")  

with tab3:     
    round_num = st.selectbox("Runde auswählen", [1, 2, 3])
    st.write(f"Partienplan für Runde {round_num}:") 

    round_matches = [m for m in st.session_state.matches if m["round"] == round_num]

    if not round_matches:
        if st.button("Paarungen generieren"):
            past_pairings = set()
            for m in st.session_state.matches:
                past_pairings.add(frozenset([m["team1"], m["team2"]]))
            unpaired = list(range(1, len(st.session_state.teams) + 1))
            random.shuffle(unpaired)

            table_num = 1
            while unpaired:
                team1 = unpaired.pop(0)
                team2 = None    
                for candidate in unpaired:
                    if frozenset([team1, candidate]) not in past_pairings:
                        team2 = candidate
                        unpaired.remove(team2)
                        break

                round_matches.append({"round": round_num, "team1": team1, "team2": team2, "table": table_num})
                table_num += 1

            st.session_state.matches.extend(round_matches)
            with open("matches.json", "w") as f:
                json.dump(st.session_state.matches, f)    

    if round_matches:
        df_matches = pd.DataFrame(round_matches)
        df_matches = df_matches[["table", "team1", "team2"]]
        df_matches.columns = ["Tisch", "Team 1", "Team 2"]
        st.dataframe(df_matches, hide_index=True)
        
        # Printable version
        if st.button("Druckversion erstellen"):
            html = """
            <html>
            <head>
                <style>
                    @page { size: A4; margin: 1cm; }
                    body { font-family: Arial, sans-serif; }
                    h2 { text-align: center; }
                    table { border-collapse: collapse; margin: 0 auto; }
                    th, td { border: 1px solid black; padding: 4px; word-wrap: break-word; }
                    .tisch { width: 2cm; text-align: center; }
                    .team { width: 8cm; }
                </style>
            </head>
            <body>
            """
            html += f"<h2>Partienplan Runde {round_num}</h2>"
            html += "<table><tr><th class='tisch'>Tisch</th><th class='team'>Team 1</th><th class='team'>Team 2</th></tr>"
            for m in round_matches:
                # Get team 1 name
                t1 = st.session_state.teams[m['team1'] - 1]
                team1_name = f"{t1['player1_last']} {t1['player1_first'][0]}. - {t1['player2_last']} {t1['player2_first'][0]}."
                
                # Get team 2 name
                t2 = st.session_state.teams[m['team2'] - 1]
                team2_name = f"{t2['player1_last']} {t2['player1_first'][0]}. - {t2['player2_last']} {t2['player2_first'][0]}."
                
                html += f"<tr><td class='tisch'>{m['table']}</td><td class='team'>{team1_name}</td><td class='team'>{team2_name}</td></tr>"
            html += "</table></body></html>"
            
            st.download_button(
                label="📄 HTML herunterladen",
                data=html,
                file_name=f"partienplan_runde_{round_num}.html",
                mime="text/html"
            )
    else:
        st.write("Noch keine Paarungen für diese Runde.")

with tab4:
    st.write("Ergebnisse eintragen:")
    
    round_num_score = st.selectbox("Runde", [1, 2, 3], key="score_round")
    round_matches_score = [m for m in st.session_state.matches if m["round"] == round_num_score]
    
    if round_matches_score:
        table_numbers = [m["table"] for m in round_matches_score]
        table_num_score = st.selectbox("Tisch", sorted(table_numbers), key="score_table")
        
        # Find the selected match
        selected_match = next((m for m in round_matches_score if m["table"] == table_num_score), None)
        
        if selected_match:
            if "scores" in selected_match:
                st.warning("Ergebnis bereits vorhanden.")
            
            st.write(f"Team {selected_match['team1']} vs Team {selected_match['team2']}")
            
            st.write("Punkte eingeben (je Runde max. 15):")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Team {selected_match['team1']}")
                r1_t1 = st.number_input("Runde 1", 0, 15, key="r1t1")
                r2_t1 = st.number_input("Runde 2", 0, 15, key="r2t1")
                r3_t1 = st.number_input("Runde 3", 0, 15, key="r3t1")
            with col2:
                st.write(f"Team {selected_match['team2']}")
                r1_t2 = st.number_input("Runde 1", 0, 15, key="r1t2")
                r2_t2 = st.number_input("Runde 2", 0, 15, key="r2t2")
                r3_t2 = st.number_input("Runde 3", 0, 15, key="r3t2")
            
            if st.button("Ergebnis speichern"):
                sub_rounds = [(r1_t1, r1_t2), (r2_t1, r2_t2), (r3_t1, r3_t2)]
                valid = True
                for i, (s1, s2) in enumerate(sub_rounds):
                    if not ((s1 == 15 and s2 < 15) or (s2 == 15 and s1 < 15)):
                        st.error(f"Runde {i+1}: Ein Team muss 15 Punkte haben, das andere weniger!")
                        valid = False
                
                if valid:
                    scores = [[r1_t1, r1_t2], [r2_t1, r2_t2], [r3_t1, r3_t2]]
                    for m in st.session_state.matches:
                        if m["round"] == round_num_score and m["table"] == table_num_score:
                            m["scores"] = scores
                            break
                    with open("matches.json", "w") as f:
                        json.dump(st.session_state.matches, f)
                    st.success("Ergebnis gespeichert!")
    else:
        st.write("Noch keine Paarungen für diese Runde.")

with tab5:
    st.write("Tabelle:")
    
    if st.session_state.teams and st.session_state.matches:
        standings = []
        
        for team_num, team in enumerate(st.session_state.teams, start=1):
            name1 = f"{team['player1_last']} {team['player1_first'][0]}." if team['player1_first'].strip() else team['player1_last']
            name2 = f"{team['player2_last']} {team['player2_first'][0]}." if team['player2_first'].strip() else team['player2_last']
            team_name = f"{name1} - {name2}"
            
            games_played = 0
            wins = 0
            losses = 0
            points_for = 0
            points_against = 0
            
            for m in st.session_state.matches:
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
                "Team": team_num,
                "Name": team_name,
                "Spiele": games_played,
                "W-L": f"{wins}-{losses}",
                "Punkte": f"{points_for}:{points_against}",
                "wins": wins,
                "losses": losses,
                "pf": points_for,
                "pa": points_against
            })
        
        standings.sort(key=lambda x: (-x["wins"], -x["pf"], x["pa"]))
        
        df_standings = pd.DataFrame(standings)[["Team", "Name", "Spiele", "W-L", "Punkte"]]
        st.dataframe(df_standings, hide_index=True)
        
        if st.button("Druckversion Tabelle erstellen"):
            html = """
            <html>
            <head>
                <style>
                    @page { size: A4; margin: 1cm; }
                    body { font-family: Arial, sans-serif; }
                    h2 { text-align: center; }
                    table { border-collapse: collapse; margin: 0 auto; }
                    th, td { border: 1px solid black; padding: 4px; word-wrap: break-word; }
                    .platz { width: 1.5cm; text-align: center; }
                    .team { width: 1.5cm; text-align: center; }
                    .name { width: 8cm; }
                    .spiele { width: 2cm; text-align: center; }
                    .punkte { width: 3cm; text-align: center; }
                </style>
            </head>
            <body>
            """
            html += "<h2>Tabelle Wattturnier SV Wörth 2025</h2>"
            html += "<table><tr><th class='platz'>Platz</th><th class='team'>Team</th><th class='name'>Name</th><th class='spiele'>Spiele</th><th class='punkte'>Punkte</th></tr>"
            
            for platz, s in enumerate(standings, start=1):
                html += f"<tr><td class='platz'>{platz}</td><td class='team'>{s['Team']}</td><td class='name'>{s['Name']}</td><td class='spiele'>{s['wins']}:{s['losses']}</td><td class='punkte'>{s['pf']}:{s['pa']}</td></tr>"
            
            html += "</table></body></html>"
            
            st.download_button(
                label="📄 HTML herunterladen",
                data=html,
                file_name="tabelle_wattturnier.html",
                mime="text/html"
            )
    else:
        st.write("Noch keine Daten vorhanden.")