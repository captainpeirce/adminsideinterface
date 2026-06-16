import streamlit as st
import plotly.graph_objects as go
import datetime, random
import pandas as pd
import db_manager as db  # Shared database link!

# ── 1. PAGE CONFIGURATION ────────────────────────────────────────────────────
st.set_page_config(
    page_title="NAVIGO — The future of Last-mile logistics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 2. INITIALIZE NAVIGATION STATE ───────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# ── 3. SIDEBAR NAVIGATION PANELS ─────────────────────────────────────────────
st.sidebar.title("NAVIGO")
st.sidebar.caption("THE FUTURE OF LOGISTICS")

# Read current database variables live
bot_data = db.get_bot_telemetry()
requests_list = db.get_all_requests()

# Live Sidebar Telemetry Badge
if bot_data["route_in_progress"]:
    st.sidebar.success(f"● TURBO: En-Route")
else:
    st.sidebar.error("● TURBO: Offline / Idle")

st.sidebar.markdown("---")

# Restored Original Sidebar Buttons
if st.sidebar.button("🏠 Home", use_container_width=True): 
    st.session_state["page"] = "Home"
if st.sidebar.button("📦 Request Delivery", use_container_width=True): 
    st.session_state["page"] = "Request Delivery"
if st.sidebar.button("📍 Live Tracking", use_container_width=True): 
    st.session_state["page"] = "Live Tracking"
if st.sidebar.button("🔔 Notifications", use_container_width=True): 
    st.session_state["page"] = "Notifications"
if st.sidebar.button("📋 Helpdesk", use_container_width=True): 
    st.session_state["page"] = "Helpdesk"
if st.sidebar.button("⭐ Feedback", use_container_width=True): 
    st.session_state["page"] = "Feedback"

# Live data calculations derived from database contents
total_orders_all_time = 284 + len(requests_list)
active_count = sum(1 for r in requests_list if r["status"] == "Pending" or r["status"] == "In Transit")

# ── 4. PAGE DISPLAY PANELS ───────────────────────────────────────────────────

# VIEW 1: HOME PAGE
if st.session_state["page"] == "Home":
    # Built-in high-contrast title card
    st.title("Meet TURBO 🚚")
    st.write("Your Autonomous Campus Delivery Companion — faster, smarter, and fully trackable. Zero waiting. Zero hassle. Pure efficiency.")
    
    # Telemetry Status Container
    c_status = st.container(border=True)
    with c_status:
        st.write(f"**Current Unit Array Status**: {bot_data['status']} | **Power Reserve**: {bot_data['battery']}% | **Completed Log Count**: {total_orders_all_time}")
        
    st.markdown("---")
    
    # Four-Metric Layout Grid Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active Deliveries", active_count if active_count > 0 else "3")
    m2.metric("Total Completed", total_orders_all_time)
    m3.metric("Avg Delivery Time", "8 min")
    m4.metric("TURBO Units", "4")
        
    st.markdown("### 📌 Core Features")
    
    # Feature Display Blocks Row
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        with st.container(border=True):
            st.markdown("**📍 Geo Tracking**\n\nReal-time live map of TURBO's exact position on campus.")
    with f2:
        with st.container(border=True):
            st.markdown("**🔒 End-to-End Security**\n\nLockable compartment + live camera. Your items, protected.")
    with f3:
        with st.container(border=True):
            st.markdown("**🔔 Smart Notifications**\n\nInstant alerts for every delivery milestone automatically.")
    with f4:
        with st.container(border=True):
            st.markdown("**🛠️ Fleet Maintenance**\n\nHealth dashboard, battery status and issue reporting.")

# VIEW 2: REQUEST DELIVERY FORM PANEL
elif st.session_state["page"] == "Request Delivery":
    st.title("📦 Log New Last-Mile Delivery")
    
    with st.form("new_delivery_form", clear_on_submit=True):
        name = st.text_input("Recipient Name", placeholder="Enter recipient's full name...")
        category = st.selectbox("Classification Type", ["Food", "Parcel", "Medical", "Documents"])
        priority = st.radio("Urgency Operational Level", ["Normal", "High", "Critical"], horizontal=True)
        pickup = st.text_input("Origin Hub (Pickup Point)", placeholder="e.g., Central Kitchen")
        dropoff = st.text_input("Destination Point (Drop-off)", placeholder="e.g., Room 302, Block C")
        
        submit_btn = st.form_submit_button("Deploy Autonomous Agent")
        
        if submit_btn:
            if name and pickup and dropoff:
                new_id = f"NAV-{random.randint(1030, 1999)}"
                now_str = datetime.datetime.now().strftime("%I:%M %p")
                
                # Commit to shared SQLite database
                db.add_request(new_id, name, category, pickup, dropoff, priority, "Pending", now_str)
                st.success(f"🚀 Sent request {new_id} to database queue!")
            else:
                st.error("⚠️ Incomplete form: Please fill out Name, Pickup, and Dropoff fields.")

# VIEW 3: LIVE TRACKING OVERVIEW
# VIEW 3: LIVE TRACKING OVERVIEW (With Live Folium Map Tracking!)
elif st.session_state["page"] == "Live Tracking":
    import folium
    from streamlit_folium import st_folium

    st.title("📍 Real-Time Location Tracker")
    
    # 🔄 LIVE AUTO-REFRESH CONTAINER (Runs background checks every 3 seconds)
    @st.fragment(run_every=3)
    def render_live_user_tracking():
        current_bot_data = db.get_bot_telemetry()
        delivery_stops = db.get_waypoints()
        
        if current_bot_data["route_in_progress"] or "Returning" in current_bot_data["status"]:
            st.success("🚚 TURBO Rover is Driving Live!")
            
            # Metric Columns Row Layout
            t1, t2 = st.columns(2)
            t1.metric(label="Current Mission Target Status", value=current_bot_data["status"])
            t2.metric(label="Rover Battery Reserve 🔋", value=f"{current_bot_data['battery']}%")
            
            # --- CUSTOMER TELEMETRY MAP INJECTION ---
            st.markdown("### 🗺️ Live Delivery Journey Tracker")
            
            # Center the map canvas right on the bot's live location points
            user_map = folium.Map(
                location=[current_bot_data["live_lat"], current_bot_data["live_lng"]], 
                zoom_start=18,
                max_zoom=21
            )
            
            # 1. Plot the Live Rover Marker Pin
            folium.Marker(
                location=[current_bot_data["live_lat"], current_bot_data["live_lng"]],
                popup=f"TURBO Rover Status: {current_bot_data['status']}",
                icon=folium.Icon(color="purple", icon="play", prefix="fa")
            ).add_to(user_map)
            
            # 2. Plot the Remaining Destination Flag Waypoints
            for idx, stop in enumerate(delivery_stops):
                # Mark past drops as gray, active target as orange, future targets as red
                flag_color = "gray" if idx < current_bot_data["current_stop_index"] else \
                             ("orange" if idx == current_bot_data["current_stop_index"] else "red")
                
                folium.Marker(
                    location=[stop[0], stop[1]],
                    popup=f"Delivery Waypoint #{idx+1}",
                    icon=folium.Icon(color=flag_color, icon="flag")
                ).add_to(user_map)
                
            # 3. Render the dynamic path line connection tracing
            if delivery_stops:
                path_lines = [[current_bot_data["live_lat"], current_bot_data["live_lng"]]] + [[s[0], s[1]] for s in delivery_stops]
                folium.PolyLine(locations=path_lines, color="#4589f5", weight=4, dash_array="6, 6").add_to(user_map)
                
            # Draw interactive map container window onto client side layout frame
            st_folium(user_map, height=440, width="100%", key="user_live_delivery_tracking_map")
            
            st.info(f"🛰️ Telemetry Node Coordinates: Lat `{current_bot_data['live_lat']:.6f}` | Lng `{current_bot_data['live_lng']:.6f}`")
        else:
            st.info("System Idle. Once the admin dispatches a route path, live telemetry updates will stream here.")

    # Fire background data query loop container function
    render_live_user_tracking()
