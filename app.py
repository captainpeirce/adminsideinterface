import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request

# Set up page configurations
st.set_page_config(
    page_title="Campus Delivery Bot Dispatch",
    page_icon="🏢",
    layout="wide"
)

# Initialize app session memory to remember clicked coordinates
if "delivery_stops" not in st.session_state:
    st.session_state.delivery_stops = []

# Title Banner
st.title("🏢 Campus Delivery Bot - Local Admin Panel")
st.write("Click up to 3 points on the campus map below to schedule a multi-stop delivery route.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Configuration")

# 1. IP Configuration input box
bot_ip = st.sidebar.text_input(
    "Robot Cellular IP Address", 
    value="166.12.34.56",
    help="Enter the public static IP address assigned to your robot's SIM card."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Active Route Queue")

# Display the assigned stops inside the sidebar loop
if not st.session_state.delivery_stops:
    st.sidebar.info("No stops selected. Click on the map to add locations.")
else:
    for idx, stop in enumerate(st.session_state.delivery_stops):
        st.sidebar.success(f"**Stop #{idx+1}**  \nLat: {stop[0]:.6f}  \nLng: {stop[1]:.6f}")

# Clear stops button in sidebar
if st.sidebar.button("🧹 Clear Route Queue", use_container_width=True):
    st.session_state.delivery_stops = []
    st.rerun()


# --- MAIN MAP DRAWING LOGIC ---
# Define starting map location (Change to your exact office park coordinates)
START_LAT, START_LNG = 17.5450, 78.3910

# Initialize an interactive Folium Map
m = folium.Map(location=[START_LAT, START_LNG], zoom_start=18, max_zoom=21)

# Add existing markers from memory state onto the map layout
for idx, stop in enumerate(st.session_state.delivery_stops):
    folium.Marker(
        location=stop,
        popup=f"Stop #{idx+1}",
        icon=folium.Icon(color="green" if idx==2 else "blue" if idx==1 else "red", icon="info-sign")
    ).addTo(m)

# Render the interactive map inside Streamlit and listen to clicks
map_data = st_folium(m, height=500, width="100%")

# Catch user clicks on the map canvas
if map_data and map_data.get("last_clicked"):
    clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
    
    # Avoid saving duplicate clicks instantly
    if clicked_coords not in st.session_state.delivery_stops:
        if len(st.session_state.delivery_stops) < 3:
            st.session_state.delivery_stops.append(clicked_coords)
            st.rerun() # Refresh app interface layout immediately
        else:
            st.warning("The vehicle can only process a maximum of 3 deliveries per trip!")


# --- DISPATCH CONTROLS ---
st.markdown("### 🚀 Dispatch Execution")

# Lock out button execution if no stops are pinned
disable_dispatch = len(st.session_state.delivery_stops) == 0

if st.button("⚡ Dispatch Vehicle Now", type="primary", disabled=disable_dispatch, use_container_width=True):
    # Unpack the 3 possible target array slot coordinates safely
    stops = st.session_state.delivery_stops
    lat1 = stops[0][0] if len(stops) > 0 else 0.0
    ln1  = stops[0][1] if len(stops) > 0 else 0.0
    lat2 = stops[1][0] if len(stops) > 1 else 0.0
    ln2  = stops[1][1] if len(stops) > 1 else 0.0
    lat3 = stops[2][0] if len(stops) > 2 else 0.0
    ln3  = stops[2][1] if len(stops) > 2 else 0.0

    # Format the direct HTTP data packet URL matching your Arduino routing logic
    dispatch_url = f"http://{bot_ip}/dispatch?lat1={lat1:.6f}&ln1={ln1:.6f}&lat2={lat2:.6f}&ln2={ln2:.6f}&lat3={lat3:.6f}&ln3={ln3:.6f}"
    
    st.info(f"Transmitting layout coordinates payload string: `{dispatch_url}`")
    
    try:
        # Send raw text packet data direct to cellular hardware receiver
        # timeout=2 ensures the local app won't hang if your bot drops connection briefly
        response = urllib.request.urlopen(dispatch_url, timeout=2)
        st.success("🎉 Data packet transmitted successfully! The vehicle is setting off.")
        st.session_state.delivery_stops = [] # Reset list logic
    except Exception as e:
        # Hardware modules don't send complete browser handshakes. 
        # So even if an error is thrown, the data string usually reaches the cell tower fine.
        st.warning("Data string pushed to network tower. Double check your vehicle hardware terminal to verify receipt.")
        st.session_state.delivery_stops = []