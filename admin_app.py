import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import time
import db_manager as db  # Shared DB Connection

st.set_page_config(
    page_title="Precinct Delivery Bot Command Center", 
    page_icon="🤖", 
    layout="wide"
)

# Pull current values from the database
bot_data = db.get_bot_telemetry()
delivery_stops = db.get_waypoints()

st.title("🛰️ Precinct Delivery Bot - Advanced Control Center")
st.write("Manage route dispatching, monitor vehicle health, and process incoming user requests live.")

# ── SIDEBAR CONFIGURATION ───────────────────────────────────────────────────
st.sidebar.header("⚙️ System Control Panel")
demo_mode = st.sidebar.toggle("🧪 Enable Demo Mode", value=True)
bot_ip = st.sidebar.text_input("Robot Cellular IP Address", value="166.12.34.56", disabled=demo_mode)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Live Telemetry Health")
st.sidebar.metric(label="Status Machine Mode", value=bot_data["status"])
st.sidebar.metric(label="Battery Reserve 🔋", value=f"{bot_data['battery']}%")

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Incoming User Requests")

# 🔄 LIVE AUTO-REFRESH CONTAINER (Runs every 4 seconds without reloading the page!)
# 🔄 LIVE AUTO-REFRESH CONTAINER (Runs every 4 seconds without reloading the page!)
@st.fragment(run_every=4)
def render_live_requests():
    # Fetch requests fresh inside the fragment container loop
    incoming_orders = db.get_all_requests()
    pending_orders = [o for o in incoming_orders if o["status"] == "Pending"]
    
    # NEW: Clear button to empty the queue table instantly
    if pending_orders:
        if st.button("🗑️ Clear All Pending Requests", use_container_width=True, type="secondary"):
            db.clear_all_requests()
            st.toast("💥 All pending user requests deleted!", icon="🗑️")
            time.sleep(0.5)
            st.rerun()
            
    st.markdown("---")
    
    if not pending_orders:
        st.info("Searching for active orders...")
    else:
        for order in pending_orders:
            with st.container(border=True):
                st.markdown(f"**ID:** `{order['id']}` | **User:** {order['name']}")
                st.markdown(f"📍 **From:** {order['pickup']}  \n🏁 **To:** {order['dropoff']}")
                
                # Button to assign this order to the bot's current path routing
                if st.button(f"✅ Approve & Route {order['id']}", key=f"btn_{order['id']}", use_container_width=True):
                    st.toast(f"Approved order {order['id']}! Click on the map to set coordinates.", icon="📌")

    
    if not pending_orders:
        st.info("Searching for active orders...")
    else:
        for order in pending_orders:
            with st.container(border=True):
                st.markdown(f"**ID:** `{order['id']}` | **User:** {order['name']}")
                st.markdown(f"📍 **From:** {order['pickup']}  \n🏁 **To:** {order['dropoff']}")
                
                # Button to assign this order to the bot's current path routing
                if st.button(f"✅ Approve & Route {order['id']}", key=f"btn_{order['id']}", use_container_width=True):
                    st.toast(f"Approved order {order['id']}! Click on the map to set coordinates.", icon="📌")
                    # We can use a session variable to handle mapping next if needed

# Execute our live background polling fragment function
render_live_requests()

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Delivery Stop Queue")
if not delivery_stops:
    st.sidebar.info("No coordinates selected. Click on the map to add waypoint drop locations.")
else:
    for idx, stop in enumerate(delivery_stops):
        st.sidebar.success(f"**Stop #{idx+1}**  \nLat: {stop[0]:.6f}  \nLng: {stop[1]:.6f}")

if st.sidebar.button("🧹 Clear Route Queue", use_container_width=True):
    db.clear_waypoints()
    db.update_bot_telemetry(17.570514, 78.432775, "🔴 Offline / Idle", "100", 0, False)
    st.toast("🧹 Route workspace cleared!", icon="🗑️")
    time.sleep(0.5)
    st.rerun()


# ── MAIN PANEL PLATFORM LAYOUT ──────────────────────────────────────────────
col_map, col_controls = st.columns(2)

with col_map:
    st.subheader("🗺️ Precinct Navigation System")
    m = folium.Map(location=[bot_data["live_lat"], bot_data["live_lng"]], zoom_start=18)

    # Draw line paths
    if delivery_stops:
        path_coordinates = [[bot_data["live_lat"], bot_data["live_lng"]]] + [[stop[0], stop[1]] for stop in delivery_stops]
        folium.PolyLine(locations=path_coordinates, color="#2563eb", weight=4, dash_array="8, 8").add_to(m)

    # Robot Marker Pin
    folium.Marker(
        location=[bot_data["live_lat"], bot_data["live_lng"]], 
        popup=f"Status: {bot_data['status']}", 
        icon=folium.Icon(color="purple", icon="play", prefix="fa")
    ).add_to(m)

    # Drop target pins
    for idx, stop in enumerate(delivery_stops):
        flag_color = "gray" if (bot_data["route_in_progress"] and idx < bot_data["current_stop_index"]) else \
                     ("orange" if (bot_data["route_in_progress"] and idx == bot_data["current_stop_index"]) else "red")
        folium.Marker(location=[stop[0], stop[1]], icon=folium.Icon(color=flag_color, icon="flag")).add_to(m)

    map_data = st_folium(m, height=480, width="100%", key="main_precinct_map")

    # Capture user mouse map clicks safely without interrupting automatic re-runs
    if map_data and map_data.get("last_clicked"):
        clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
        if clicked_coords not in delivery_stops and not bot_data["route_in_progress"]:
            if len(delivery_stops) < 3:
                db.add_waypoint(clicked_coords[0], clicked_coords[1])
                st.toast(f"📍 Stop pinned!", icon="📌")
                time.sleep(0.5)
                st.rerun()

with col_controls:
    st.subheader("🚨 Control Actions")
    if st.button("🛑 EMERGENCY KILL SWITCH", type="primary", use_container_width=True):
        db.update_bot_telemetry(bot_data["live_lat"], bot_data["live_lng"], "🛑 EMERGENCY HALT", bot_data["battery"], bot_data["current_stop_index"], False)
        st.toast("🚨 EMERGENCY HALT BROADCASTED!", icon="🛑")
        st.rerun()

    st.markdown("---")
    st.markdown("### 🚀 Dispatch Mode")
    disable_dispatch = len(delivery_stops) == 0 or bot_data["route_in_progress"]
    
    if st.button("⚡ Launch Route Path", disabled=disable_dispatch, use_container_width=True):
        db.update_bot_telemetry(bot_data["live_lat"], bot_data["live_lng"], "🟢 Navigating Stop 1", bot_data["battery"], 0, True)
        st.toast("🚀 Rover mission launched!", icon="🛰️")
        time.sleep(0.5)
        st.rerun()

    # Progress Tracking Progress Bars
    if bot_data["route_in_progress"] and delivery_stops:
        total_stops = len(delivery_stops)
        curr_idx = bot_data["current_stop_index"]
        st.progress(float(curr_idx) / float(total_stops), text=f"Waypoints: {curr_idx} of {total_stops} complete")
        
        if demo_mode and curr_idx < total_stops:
            if st.button("🙋‍♂️ Simulate Customer Pickup (Advance Bot)", use_container_width=True):
                target = delivery_stops[curr_idx]
                next_idx = curr_idx + 1
                new_status = "🏁 Route Completed" if next_idx >= total_stops else f"🟢 Navigating Stop {next_idx + 1}"
                new_progress = False if next_idx >= total_stops else True
                next_battery = str(max(0, int(bot_data["battery"]) - 5))
                
                db.update_bot_telemetry(target[0], target[1], new_status, next_battery, next_idx, new_progress)
                st.toast("✓ Bot advanced to target destination!", icon="🚚")
                time.sleep(0.5)
                st.rerun()
