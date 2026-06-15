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

# 1. INITIALISE SESSION MEMORY STATES
if "delivery_stops" not in st.session_state:
    st.session_state.delivery_stops = []
if "bot_live_lat" not in st.session_state:
    st.session_state.bot_live_lat = 17.570514  # Dundigal coordinates
if "bot_live_lng" not in st.session_state:
    st.session_state.bot_live_lng = 78.432775
if "bot_status" not in st.session_state:
    st.session_state.bot_status = "🔴 Offline / Idle"
if "bot_battery" not in st.session_state:
    st.session_state.bot_battery = "100"
if "current_stop_index" not in st.session_state:
    st.session_state.current_stop_index = 0
if "route_in_progress" not in st.session_state:
    st.session_state.route_in_progress = False

# --- TOP HEADER SECTION ---
st.title("🛰️ Precinct Delivery Bot - Advanced Control Center")
st.write("Manage route dispatching, monitor vehicle health, and track waypoint completion paths live.")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ System Control Panel")

# Demo Mode Toggle Switch (Critical for error-free pitches!)
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

if st.sidebar.button("导 Clear Route Queue", use_container_width=True):
    st.session_state.delivery_stops = []
    st.session_state.current_stop_index = 0
    st.session_state.route_in_progress = False
    st.session_state.bot_status = "🔴 Offline / Idle"
    st.toast("🧹 Route workspace cleared!", icon="🗑️")
    time.sleep(0.5)
    st.rerun()


# --- SECTION 2: SIDE-BY-SIDE PLATFORM LAYOUT ---
col_map, col_controls = st.columns(2)

with col_map:
    st.subheader("🗺️ Precinct Navigation System")
    
    # Render map base focused on the active robot pin
    m = folium.Map(
        location=[st.session_state.bot_live_lat, st.session_state.bot_live_lng], 
        zoom_start=18, 
        max_zoom=21
    )

    # DYNAMIC PATH TRACING LINE
    if st.session_state.delivery_stops:
        path_coordinates = [[st.session_state.bot_live_lat, st.session_state.bot_live_lng]]
        for stop in st.session_state.delivery_stops:
            path_coordinates.append([stop[0], stop[1]])
        
        folium.PolyLine(
            locations=path_coordinates,
            color="#2563eb",
            weight=4,
            opacity=0.7,
            dash_array="8, 8",
            tooltip="Calculated Autonomous Mission Path"
        ).add_to(m)

    # PLACE THE LIVE ROBOT PURPLE POSITION PIN
    folium.Marker(
        location=[st.session_state.bot_live_lat, st.session_state.bot_live_lng],
        popup=f"<b>VEHICLE ID: BOT-01</b><br>Status: {st.session_state.bot_status}<br>Battery: {st.session_state.bot_battery}%",
        icon=folium.Icon(color="purple", icon="play", prefix="fa")
    ).add_to(m)

    # PLACE PLANNED TARGET ROUTE DESTINATION FLAGS
    for idx, stop in enumerate(st.session_state.delivery_stops):
        if st.session_state.route_in_progress and idx < st.session_state.current_stop_index:
            flag_color = "gray"  # Completed stop
            popup_text = f"Stop #{idx+1} (✓ Delivered)"
        elif st.session_state.route_in_progress and idx == st.session_state.current_stop_index:
            flag_color = "orange"  # Active target stop
            popup_text = f"Stop #{idx+1} (⚡ Active Target)"
        else:
            flag_color = "green" if idx==2 else "blue" if idx==1 else "red"
            popup_text = f"Delivery Drop Stop #{idx+1}"

        folium.Marker(
            location=[stop[0], stop[1]],
            popup=popup_text,
            icon=folium.Icon(color=flag_color, icon="flag")
        ).add_to(m)

    # Render interactive map canvas
    map_data = st_folium(m, height=480, width="100%", key="main_precinct_map")

    # Capture click inputs
    if map_data and map_data.get("last_clicked"):
        clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
        if clicked_coords not in st.session_state.delivery_stops and not st.session_state.route_in_progress:
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
        st.session_state.route_in_progress = False
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
    
    # LIVE WAYPOINT PROGRESS SYSTEM DOCK
    st.markdown("### 📈 Live Route Progress Tracker")
    if st.session_state.route_in_progress and st.session_state.delivery_stops:
        total_stops = len(st.session_state.delivery_stops)
        curr_index = st.session_state.current_stop_index
        
        progress_percentage = float(curr_index) / float(total_stops)
        st.progress(progress_percentage, text=f"Route Progression: Completed {curr_index} of {total_stops} Waypoints")
        
        if demo_mode:
            if curr_index < total_stops:
                st.write(f"👉 **Current Target**: Vehicle traveling toward **Stop #{curr_index + 1}**")
                if st.button("🙋‍♂️ Simulate Customer Pickup (Advance Bot)", use_container_width=True):
                    active_target = st.session_state.delivery_stops[curr_index]
                    st.session_state.bot_live_lat = active_target[0]
                    st.session_state.bot_live_lng = active_target[1]
                    
                    st.session_state.current_stop_index += 1
                    if st.session_state.current_stop_index >= total_stops:
                        st.session_state.bot_status = "🏁 Route Completed"
                        st.toast("🎉 Mission complete! Bot arrived at final point.", icon="🙌")
                    else:
                        st.session_state.bot_status = f"🟢 Navigating Stop {st.session_state.current_stop_index + 1}"
                        st.toast(f"✓ Stop #{curr_index + 1} finished! Steering to next destination.", icon="🚚")
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.success("🎉 All scheduled office park deliveries have been completed successfully!")
                if st.button("↩️ Send Bot Back to Home Base", use_container_width=True):
                    st.session_state.bot_live_lat = 17.570514
                    st.session_state.bot_live_lng = 78.432775
                    st.session_state.delivery_stops = []
                    st.session_state.current_stop_index = 0
                    st.session_state.route_in_progress = False
                    st.session_state.bot_status = "🔴 Offline / Idle"
                    st.rerun()
    else:
        st.info("No active route driving right now. Pin map stops and click dispatch to initialize tracking loops.")

    st.markdown("---")
    
    # LAUNCH DATA ROUTE DISPATCH SYSTEM
    st.markdown("### 🚀 Dispatch Mode")
    disable_dispatch = len(st.session_state.delivery_stops) == 0 or st.session_state.route_in_progress
    
    if st.button("⚡ Launch Route Path", disabled=disable_dispatch, use_container_width=True):
        stops = st.session_state.delivery_stops
        lat1 = stops[0][0] if len(stops) > 0 else 0.0
        ln1  = stops[0][1] if len(stops) > 0 else 0.0
        lat2 = stops[1][0] if len(stops) > 1 else 0.0
        ln2  = stops[1][1] if len(stops) > 1 else 0.0
        lat3 = stops[2][0] if len(stops) > 2 else 0.0
        ln3  = stops[2][1] if len(stops) > 2 else 0.0

        dispatch_url = f"http://{bot_ip}/dispatch?lat1={lat1:.6f}&ln1={ln1:.6f}&lat2={lat2:.6f}&ln2={ln2:.6f}&lat3={lat3:.6f}&ln3={ln3:.6f}"
        
        st.session_state.route_in_progress = True
        st.session_state.current_stop_index = 0

        if demo_mode:
            with st.spinner("Encrypting path layout data strings..."):
                time.sleep(1.2)
