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

with tab2: 
    st.write("Angemeldete Teams:")
    df = pd.DataFrame(st.session_state.teams)
    df.index += 1  # Start index at 1 instead of 0
    df.columns = ["Vorname 1", "Nachname 1", "Vorname 2", "Nachname 2"]

    # Show editable table
    edited_df = st.data_editor(df)
    edited_df.columns = ["player1_first", "player1_last", "player2_first", "player2_last"]

    if st.button("Aktualisieren"):
        st.session_state.teams = edited_df.to_dict(orient="records")
        with open("teams.json", "w") as f:
            json.dump(st.session_state.teams, f)
        st.write("Teilnehmerliste aktualisiert.")   

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
        st.dataframe(df_matches)
    else:
        st.write("Noch keine Paarungen für diese Runde.")

with tab4:
    st.write("Ergebnisse eintragen:")

