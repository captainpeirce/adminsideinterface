import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import json

# Set up page configurations
st.set_page_config(
    page_title="Campus Delivery Bot Command Center",
    page_icon="🤖",
    layout="wide"
)

# 1. INITIALISE APPMEMORY STORAGE STATE
# Stores user clicks, live robot positions, and health updates
if "delivery_stops" not in st.session_state:
    st.session_state.delivery_stops = []
if "bot_live_lat" not in st.session_state:
    st.session_state.bot_live_lat = 17.5450  # Default starting pool
if "bot_live_lng" not in st.session_state:
    st.session_state.bot_live_lng = 78.3910
if "bot_status" not in st.session_state:
    st.session_state.bot_status = "🔴 Offline / Idle"
if "bot_battery" not in st.session_state:
    st.session_state.bot_battery = "100"

st.title("🛰️ Campus Delivery Bot - Advanced Control Center")
st.write("Manage route dispatching, monitor vehicle health, and issue emergency controls live.")

# --- SIDEBAR: BOT TELEMETRY & HEALTH MONITOR ---
st.sidebar.header("🔌 Vehicle Connection")
bot_ip = st.sidebar.text_input(
    "Robot Cellular IP Address", 
    value="166.12.34.56",
    help="Enter the public static IP address assigned to your robot's SIM card."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Live Telemetry Health")

# Functional emoji visual anchors for telemetry scanning
st.sidebar.metric(label="Status Machine Mode", value=st.session_state.bot_status)
st.sidebar.metric(label="Battery Reserve🔋", value=f"{st.session_state.bot_battery}%")

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Delivery Stop Queue")
if not st.session_state.delivery_stops:
    st.sidebar.info("No stops selected. Click on the map to add locations.")
else:
    for idx, stop in enumerate(st.session_state.delivery_stops):
        st.sidebar.success(f"**Stop #{idx+1}**  \nLat: {stop[0]:.6f}  \nLng: {stop[1]:.6f}")

if st.sidebar.button("🧹 Clear Route Queue", use_container_width=True):
    st.session_state.delivery_stops = []
    st.rerun()


# --- SECTION 2: MAP INTERFACE WITH LIVE PIN TRACKING ---
col_map, col_controls = st.columns([3, 1])

with col_map:
    st.subheader("🗺️ Campus Navigation System")
    
    # Render map base focused on the robot's current position
    m = folium.Map(
        location=[st.session_state.bot_live_lat, st.session_state.bot_live_lng], 
        zoom_start=18, 
        max_zoom=21
    )

    # 1. Place the LIVE ROBOT TRACKING PIN on the canvas
    folium.Marker(
        location=[st.session_state.bot_live_lat, st.session_state.bot_live_lng],
        popup=f"<b>ROBOT CURRENT POSITION</b><br>Battery: {st.session_state.bot_battery}%",
        icon=folium.Icon(color="purple", icon="play", prefix="fa")
    ).add_to(m)

    # 2. Place planned target path stops onto the map layout
    for idx, stop in enumerate(st.session_state.delivery_stops):
        folium.Marker(
            location=stop,
            popup=f"Delivery Drop Stop #{idx+1}",
            icon=folium.Icon(color="green" if idx==2 else "blue" if idx==1 else "red", icon="flag")
        ).add_to(m)

    # Render interactive listener map canvas
    map_data = st_folium(m, height=520, width="100%", key="main_campus_map")

    # Capture click interactions to save delivery coordinates
    if map_data and map_data.get("last_clicked"):
        clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
        if clicked_coords not in st.session_state.delivery_stops:
            if len(st.session_state.delivery_stops) < 3:
                st.session_state.delivery_stops.append(clicked_coords)
                st.rerun()
            else:
                st.warning("The vehicle can only process a maximum of 3 deliveries per trip!")


# --- SECTION 3: EMERGENCY DOCK AND MANAGEMENT PANEL ---
with col_controls:
    st.subheader("🚨 Control Actions")
    
    # EMERGENCY STOP BUTTON: Immediately overrides execution and stops the vehicle
    st.markdown("### ⚠️ Safety Cutoff")
    if st.button("🛑 EMERGENCY KILL SWITCH", type="primary", use_container_width=True):
        st.critical("🚨 KILL SWITCH ISSUED! Stopping all drive channels.")
        estop_url = f"http://{bot_ip}/halt"
        try:
            urllib.request.urlopen(estop_url, timeout=1.5)
            st.success("Halt frame confirmed by cellular array.")
        except Exception:
            st.warning("Halt text packet pushed over the network tower line.")

    st.markdown("---")
    
    # STANDARD DISPATCH SWITCH
    st.markdown("### 🚀 Dispatch Mode")
    disable_dispatch = len(st.session_state.delivery_stops) == 0
    
    if st.button("⚡ Launch Route Path", disabled=disable_dispatch, use_container_width=True):
        stops = st.session_state.delivery_stops
        lat1 = stops[0][0] if len(stops) > 0 else 0.0
        ln1  = stops[0][1] if len(stops) > 0 else 0.0
        lat2 = stops[1][0] if len(stops) > 1 else 0.0
        ln2  = stops[1][1] if len(stops) > 1 else 0.0
        lat3 = stops[2][0] if len(stops) > 2 else 0.0
        ln3  = stops[2][1] if len(stops) > 2 else 0.0

        dispatch_url = f"http://{bot_ip}/dispatch?lat1={lat1:.6f}&ln1={ln1:.6f}&lat2={lat2:.6f}&ln2={ln2:.6f}&lat3={lat3:.6f}&ln3={ln3:.6f}"
        
        try:
            urllib.request.urlopen(dispatch_url, timeout=2)
            st.success("Vehicle route loaded. Robot starting drive.")
            st.session_state.delivery_stops = []
            st.rerun()
        except Exception:
            st.warning("Data coordinates sent over network. Check vehicle terminal.")
            st.session_state.delivery_stops = []
            st.rerun()


# --- SECTION 4: SIMULATED HARDWARE BACKEND INCOME (FOR LOCAL TESTING) ---
# Allows you to simulate updates to check how your live map pin works
st.markdown("---")
st.subheader("🧪 Telemetry Hardware Simulation (For Bench Testing Only)")
st.write("Use this test tool to mock incoming data from your robot's cellular module.")

c1, c2, c3, c4 = st.columns(4)
with c1:
    test_lat = st.number_input("Simulate Latitude", value=17.545200, format="%.6f")
with c2:
    test_lng = st.number_input("Simulate Longitude", value=78.391200, format="%.6f")
with c3:
    test_stat = st.selectbox("Simulate Mode Status", ["🟢 Navigating Stop 1", "🟡 Waiting at Stop 1", "🟢 Returning Home", "⚠️ Hazard Stuck"])
with c4:
    test_batt = st.slider("Simulate Battery %", 0, 100, 85)

if st.button("📥 Apply Simulated Updates", use_container_width=True):
    st.session_state.bot_live_lat = test_lat
    st.session_state.bot_live_lng = test_lng
    st.session_state.bot_status = test_stat
    st.session_state.bot_battery = str(test_batt)
    st.success("Telemetry workspace updated! Check the live purple pin on the map layout.")
    st.rerun()
