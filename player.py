import streamlit as st
import json
import pandas as pd
import gspread
from datetime import datetime
import os
from datetime import timedelta

def get_orders_sheet():
    try:
        # Try Streamlit Cloud secrets first
        creds = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(dict(creds))
    except:
        # Fall back to local file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        creds_path = os.path.join(script_dir, "credentials.json")
        gc = gspread.service_account(filename=creds_path)
    
    sh = gc.open("bestellungen_wt")
    return sh.sheet1

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

tab1, tab2, tab3 = st.tabs(["📊 Tabelle", "🎯 Mein Tisch", "🍺 Speisekarte/Bestellung"])

with tab1:
    st.write("**Aktuelle Tabelle:**")
    
    if teams and matches:
        standings = []
        
        for team_num, team in enumerate(teams, start=1):
            name1 = f"{team['player1_last']} {team['player1_first'][0]}." if team['player1_first'].strip() else team['player1_last']
            name2 = f"{team['player2_last']} {team['player2_first'][0]}." if team['player2_first'].strip() else team['player2_last']
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
    st.write("**🍺 Bestellung aufgeben:**")
    
    tisch_nr = st.text_input("Tischnummer", "")
    
    # Define prices
    prices = {
        "helles": 3.50, "radler": 3.50, "weissbier": 3.50, "weissbier_af": 3.50,
        "weinschorle_suess": 3.50, "weinschorle_sauer": 3.50,
        "spezi": 3.00, "apfelschorle": 3.00, "wasser": 2.50,
        "kaffee": 2.00,
        "goassmass": 8.00, "ruescherl": 5.00, "schnaps_haselnuss": 3.00, 
        "schnaps_willy": 3.00, "schnapsbrettl": 10.00,
        "salamisemmel": 2.50, "leberkaesesemmel": 2.50, "kaesesemmel": 2.50,
        "pizza_salami": 3.50, "pizza_margherita": 3.50
    }
    
    st.write("**🍺 Bier:**")
    col1, col2 = st.columns(2)
    with col1:
        helles = st.number_input("Helles (3,50€)", min_value=0, max_value=20, value=0, key="helles")
        radler = st.number_input("Radler (3,50€)", min_value=0, max_value=20, value=0, key="radler")
    with col2:
        weissbier = st.number_input("Weißbier (3,50€)", min_value=0, max_value=20, value=0, key="weissbier")
        weissbier_af = st.number_input("Weißbier alkoholfrei (3,50€)", min_value=0, max_value=20, value=0, key="weissbier_af")
    
    st.write("**🍷 Wein & Softdrinks:**")
    col1, col2 = st.columns(2)
    with col1:
        weinschorle_suess = st.number_input("Weinschorle süß (3,50€)", min_value=0, max_value=20, value=0, key="weinschorle_suess")
        weinschorle_sauer = st.number_input("Weinschorle sauer (3,50€)", min_value=0, max_value=20, value=0, key="weinschorle_sauer")
        spezi = st.number_input("Spezi (3,00€)", min_value=0, max_value=20, value=0, key="spezi")
    with col2:
        apfelschorle = st.number_input("Apfelschorle (3,00€)", min_value=0, max_value=20, value=0, key="apfelschorle")
        wasser = st.number_input("Wasser medium (2,50€)", min_value=0, max_value=20, value=0, key="wasser")
        kaffee = st.number_input("Haferl Kaffee (2,00€)", min_value=0, max_value=20, value=0, key="kaffee")
    
    st.write("**🥃 Schnaps & Spezialitäten:**")
    col1, col2 = st.columns(2)
    with col1:
        goassmass = st.number_input("Goaßmaß (8,00€)", min_value=0, max_value=20, value=0, key="goassmass")
        ruescherl = st.number_input("Rüscherl (5,00€)", min_value=0, max_value=20, value=0, key="ruescherl")
        schnaps_haselnuss = st.number_input("Schnaps Haselnuss (3,00€)", min_value=0, max_value=20, value=0, key="schnaps_haselnuss")
    with col2:
        schnaps_willy = st.number_input("Schnaps Willy (3,00€)", min_value=0, max_value=20, value=0, key="schnaps_willy")
        schnapsbrettl = st.number_input("Schnapsbrettl 4x2cl (10,00€)", min_value=0, max_value=10, value=0, key="schnapsbrettl")
    
    # Schnapsbrettl combination selector
    brettl_combo = None
    if schnapsbrettl > 0:
        brettl_combo = st.selectbox("Schnapsbrettl Kombination:", [
            "4x Haselnuss",
            "3x Haselnuss + 1x Willy",
            "2x Haselnuss + 2x Willy",
            "1x Haselnuss + 3x Willy",
            "4x Willy"
        ], key="brettl_combo")
    
    st.write("**🍕 Essen:**")
    col1, col2 = st.columns(2)
    with col1:
        salamisemmel = st.number_input("Salamisemmel (2,50€)", min_value=0, max_value=20, value=0, key="salamisemmel")
        leberkaesesemmel = st.number_input("Leberkäsesemmel (2,50€)", min_value=0, max_value=20, value=0, key="leberkaesesemmel")
        kaesesemmel = st.number_input("Käsesemmel (2,50€)", min_value=0, max_value=20, value=0, key="kaesesemmel")
    with col2:
        pizza_salami = st.number_input("Pizzastück Salami (3,50€)", min_value=0, max_value=20, value=0, key="pizza_salami")
        pizza_margherita = st.number_input("Pizzastück Margherita (3,50€)", min_value=0, max_value=20, value=0, key="pizza_margherita")
    
    # Calculate total
    total = (helles * prices["helles"] + radler * prices["radler"] + 
             weissbier * prices["weissbier"] + weissbier_af * prices["weissbier_af"] +
             weinschorle_suess * prices["weinschorle_suess"] + weinschorle_sauer * prices["weinschorle_sauer"] +
             spezi * prices["spezi"] + apfelschorle * prices["apfelschorle"] + wasser * prices["wasser"] +
             kaffee * prices["kaffee"] + goassmass * prices["goassmass"] + ruescherl * prices["ruescherl"] +
             schnaps_haselnuss * prices["schnaps_haselnuss"] + schnaps_willy * prices["schnaps_willy"] +
             schnapsbrettl * prices["schnapsbrettl"] +
             salamisemmel * prices["salamisemmel"] + leberkaesesemmel * prices["leberkaesesemmel"] +
             kaesesemmel * prices["kaesesemmel"] + pizza_salami * prices["pizza_salami"] + 
             pizza_margherita * prices["pizza_margherita"])
    
    if total > 0:
        st.info(f"💰 Gesamtpreis: {total:.2f} €")
    
    if st.button("🛒 Bestellung absenden"):
        if not tisch_nr:
            st.error("Bitte Tischnummer eingeben!")
        else:
            items = []
            if helles > 0: items.append(f"{helles}x Helles")
            if radler > 0: items.append(f"{radler}x Radler")
            if weissbier > 0: items.append(f"{weissbier}x Weißbier")
            if weissbier_af > 0: items.append(f"{weissbier_af}x Weißbier alk.frei")
            if weinschorle_suess > 0: items.append(f"{weinschorle_suess}x Weinschorle süß")
            if weinschorle_sauer > 0: items.append(f"{weinschorle_sauer}x Weinschorle sauer")
            if spezi > 0: items.append(f"{spezi}x Spezi")
            if apfelschorle > 0: items.append(f"{apfelschorle}x Apfelschorle")
            if wasser > 0: items.append(f"{wasser}x Wasser")
            if kaffee > 0: items.append(f"{kaffee}x Kaffee")
            if goassmass > 0: items.append(f"{goassmass}x Goaßmaß")
            if ruescherl > 0: items.append(f"{ruescherl}x Rüscherl")
            if schnaps_haselnuss > 0: items.append(f"{schnaps_haselnuss}x Schnaps Haselnuss")
            if schnaps_willy > 0: items.append(f"{schnaps_willy}x Schnaps Willy")
            if schnapsbrettl > 0: items.append(f"{schnapsbrettl}x Schnapsbrettl ({brettl_combo})")
            if salamisemmel > 0: items.append(f"{salamisemmel}x Salamisemmel")
            if leberkaesesemmel > 0: items.append(f"{leberkaesesemmel}x Leberkäsesemmel")
            if kaesesemmel > 0: items.append(f"{kaesesemmel}x Käsesemmel")
            if pizza_salami > 0: items.append(f"{pizza_salami}x Pizza Salami")
            if pizza_margherita > 0: items.append(f"{pizza_margherita}x Pizza Margherita")
            
            if not items:
                st.error("Bitte mindestens einen Artikel auswählen!")
            else:
                sheet = get_orders_sheet()
                order_id = len(sheet.get_all_values())
                bestellung = ", ".join(items)
                zeit = (datetime.now() + timedelta(hours=1)).strftime("%H:%M:%S")
                preis = f"{total:.2f} €"
                
                sheet.append_row([order_id, tisch_nr, bestellung, zeit, preis, "offen"])
                st.toast("✅ Bestellung erfasst!", icon="🍺")
