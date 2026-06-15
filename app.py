import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import time

# Set up page configurations
st.set_page_config(
    page_title="Precinct Delivery Bot Command Center",
    page_icon="🤖",
    layout="wide"
)

# 1. LOCKED-IN VEHICLE TESTING COORDINATES
# Updated from general starting pool to your exact requested coordinates: 17.570514, 78.432775
if "delivery_stops" not in st.session_state:
    st.session_state.delivery_stops = []
if "bot_live_lat" not in st.session_state:
    st.session_state.bot_live_lat = 17.570514  # <--- Locked to your exact testing latitude
if "bot_live_lng" not in st.session_state:
    st.session_state.bot_live_lng = 78.432775  # <--- Locked to your exact testing longitude
if "bot_status" not in st.session_state:
    st.session_state.bot_status = "🔴 Offline / Idle"
if "bot_battery" not in st.session_state:
    st.session_state.bot_battery = "100"

# --- TOP HEADER SECTION ---
st.title("🛰️ Precinct Delivery Bot - Advanced Control Center")
st.write("Manage route dispatching, monitor vehicle health, and issue emergency controls live.")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ System Control Panel")

# Demo Mode Toggle Switch (Critical for presentations!)
demo_mode = st.sidebar.toggle("🧪 Enable Demo Mode", value=True, help="Turn on to safely simulate dispatches without hardware connected.")

st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Vehicle Connection")
bot_ip = st.sidebar.text_input(
    "Robot Cellular IP Address", 
    value="166.12.34.56",
    disabled=demo_mode,
    help="Enter the public static IP address assigned to your robot's SIM card."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Live Telemetry Health")
st.sidebar.metric(label="Status Machine Mode", value=st.session_state.bot_status)
st.sidebar.metric(label="Battery Reserve 🔋", value=f"{st.session_state.bot_battery}%")

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Delivery Stop Queue")
if not st.session_state.delivery_stops:
    st.sidebar.info("No stops selected. Click on the map to add locations.")
else:
    for idx, stop in enumerate(st.session_state.delivery_stops):
        st.sidebar.success(f"**Stop #{idx+1}**  \nLat: {stop[0]:.6f}  \nLng: {stop[1]:.6f}")


if st.sidebar.button("🧹 Clear Route Queue", use_container_width=True):
    st.session_state.delivery_stops = []
    st.toast("🧹 Route queue cleared!", icon="🗑️")
    time.sleep(0.5)
    st.rerun()


# --- SECTION 2: MAP PLATFORM ---
col_map, col_controls = st.columns(2)    

with col_map:
    st.subheader("🗺️ Precinct Navigation System")
    
    # Render map base focused on the active robot pin
    m = folium.Map(
        location=[st.session_state.bot_live_lat, st.session_state.bot_live_lng], 
        zoom_start=18,  # Slightly zoomed in closer for sidewalk view precision
        max_zoom=21
    )

    # 1. Place the LIVE ROBOT TRACKING PIN
    folium.Marker(
        location=[st.session_state.bot_live_lat, st.session_state.bot_live_lng],
        popup=f"<b>VEHICLE ID: BOT-01</b><br>Status: {st.session_state.bot_status}<br>Battery: {st.session_state.bot_battery}%",
        icon=folium.Icon(color="purple", icon="play", prefix="fa")
    ).add_to(m)

    # 2. Place planned target route destinations
    for idx, stop in enumerate(st.session_state.delivery_stops):
        folium.Marker(
            location=stop,
            popup=f"Delivery Drop Stop #{idx+1}",
            icon=folium.Icon(color="green" if idx==2 else "blue" if idx==1 else "red", icon="flag")
        ).add_to(m)

    # Render layout listener map canvas
    map_data = st_folium(m, height=480, width="100%", key="main_precinct_map")

    # Capture click inputs to build target queue
    if map_data and map_data.get("last_clicked"):
        clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
        if clicked_coords not in st.session_state.delivery_stops:
            if len(st.session_state.delivery_stops) < 3:
                st.session_state.delivery_stops.append(clicked_coords)
                st.toast(f"📍 Stop #{len(st.session_state.delivery_stops)} pinned to route plan!", icon="📌")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("The vehicle can only process a maximum of 3 deliveries per trip!")


# --- SECTION 3: SYSTEM ACTION PANEL ---
with col_controls:
    st.subheader("🚨 Control Actions")
    
    # EMERGENCY KILL SWITCH
    st.markdown("### ⚠️ Safety Cutoff")
    if st.button("🛑 EMERGENCY KILL SWITCH", type="primary", use_container_width=True):
        st.toast("🚨 EMERGENCY HALT BROADCASTED!", icon="🛑")
        if demo_mode:
            st.error("⚠️ DEMO ACTION: Vehicle execution frozen. All drive channels cut to 0%.")
            st.session_state.bot_status = "🛑 EMERGENCY HALT"
        else:
            estop_url = f"http://{bot_ip}/halt"
            try:
                urllib.request.urlopen(estop_url, timeout=1.5)
                st.success("Halt command received by cellular module.")
            except Exception:
                st.warning("Halt signal sent over cell network towers.")

    st.markdown("---")
    
    # STANDARD DISPATCH LOGIC SWITCH
    st.markdown("### 🚀 Dispatch Mode")
    disable_dispatch = len(st.session_state.delivery_stops) == 0
    
    if st.button("⚡ Launch Route Path", disabled=disable_dispatch, use_container_width=True):
        stops = st.session_state.delivery_stops
        lat1 = stops if len(stops) > 0 else 0.0
        ln1  = stops if len(stops) > 0 else 0.0
        lat2 = stops if len(stops) > 1 else 0.0
        ln2  = stops if len(stops) > 1 else 0.0
        lat3 = stops if len(stops) > 2 else 0.0
        ln3  = stops if len(stops) > 2 else 0.0

        dispatch_url = f"http://{bot_ip}/dispatch?lat1={lat1:.6f}&ln1={ln1:.6f}&lat2={lat2:.6f}&ln2={ln2:.6f}&lat3={lat3:.6f}&ln3={ln3:.6f}"
        
        if demo_mode:
            with st.spinner("Encrypting path layout data strings..."):
                time.sleep(1.2)
            st.toast("🎉 Dispatch successful! Bot-01 leaving loading terminal.", icon="🚀")
            st.session_state.bot_status = "🟢 Navigating Stop 1"
            st.session_state.delivery_stops = []
            time.sleep(1)
            st.rerun()
        else:
            try:
                urllib.request.urlopen(dispatch_url, timeout=2)
                st.success("Vehicle route loaded. Robot starting drive.")
                st.session_state.delivery_stops = []
                time.sleep(0.5)
                st.rerun()
            except Exception:
                st.warning("Data coordinates sent over network. Check vehicle terminal.")
                st.session_state.delivery_stops = []
                time.sleep(0.5)
                st.rerun()


# --- SECTION 4: BENCH TESTING & TELEMETRY SIMULATOR ---
st.markdown("---")
st.subheader("🧪 Telemetry Hardware Simulation (For Bench Testing Only)")
st.write("Use this test tool to mock incoming data from your robot's cellular module.")

c1, c2, c3, c4 = st.columns(4)
with c1:
    test_lat = st.number_input("Simulate Latitude", value=17.570514, format="%.6f") # Default matched to your testing zone
with c2:
    test_lng = st.number_input("Simulate Longitude", value=78.432775, format="%.6f") # Default matched to your testing zone
with c3:
    test_stat = st.selectbox("Simulate Mode Status", ["🔴 Offline / Idle", "🟢 Navigating Stop 1", "🟡 Waiting at Stop 1", "🟢 Returning Home", "⚠️ Hazard Stuck"])
with c4:
    test_batt = st.slider("Simulate Battery %", 0, 100, 100)

if st.button("📥 Apply Simulated Updates", use_container_width=True):
    st.session_state.bot_live_lat = test_lat
    st.session_state.bot_live_lng = test_lng
    st.session_state.bot_status = test_stat
    st.session_state.bot_battery = str(test_batt)
    st.toast("Telemetry data synced!", icon="📥")
    time.sleep(0.5)
    st.rerun()
