import streamlit as st
import gspread
import os
from datetime import datetime



st.set_page_config(page_title="Ausschank - Wattturnier", layout="wide")

# Auto-refresh every 30 seconds
st.markdown("""
    <meta http-equiv="refresh" content="30">
""", unsafe_allow_html=True)

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
st.title("Ausschank - Bestellungen")

# Refresh button
if st.button("🔄 Aktualisieren"):
    st.rerun()

# Load orders
sheet = get_orders_sheet()
all_orders = sheet.get_all_records()

# Split into open and done
open_orders = [o for o in all_orders if o["Status"] == "offen"]
done_orders = [o for o in all_orders if o["Status"] == "erledigt"]

# Check for new orders and play sound
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = len(all_orders)

if len(all_orders) > st.session_state.last_order_count:
    st.markdown("""
        <audio autoplay>
            <source src="https://www.soundjay.com/buttons/beep-07a.mp3" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)
    st.toast("🆕 Neue Bestellung!", icon="🔔")

st.session_state.last_order_count = len(all_orders)

# Display open orders
st.subheader(f"📋 Offene Bestellungen ({len(open_orders)})")

if open_orders:
    for order in open_orders:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.write(f"**Tisch {order['Tischnummer']}**")
                st.write(f"🕐 {order['Zeit']}")
            with col2:
                st.write(f"**{order['Bestellung']}**")
                st.write(f"💰 {order['Preis']}")
            with col3:
                if st.button("✅ Erledigt", key=f"done_{order['Order ID']}"):
                    # Find row and update status
                    cell = sheet.find(str(order['Order ID']))
                    sheet.update_cell(cell.row, 6, "erledigt")
                    st.rerun()
            st.divider()
else:
    st.info("Keine offenen Bestellungen! 🎉")

# Show completed orders (collapsed)
with st.expander(f"✅ Erledigte Bestellungen ({len(done_orders)})"):
    for order in done_orders:
        st.write(f"Tisch {order['Tischnummer']}: {order['Bestellung']} ({order['Zeit']})")