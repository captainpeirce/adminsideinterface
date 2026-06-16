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
# VIEW 3: LIVE TRACKING OVERVIEW (With background auto-refresh!)
elif st.session_state["page"] == "Live Tracking":
    st.title("📍 Real-Time Location Tracker")
    
    # 🔄 LIVE AUTO-REFRESH CONTAINER (Checks the database every 3 seconds for bot updates!)
    @st.fragment(run_every=3)
    def render_live_user_tracking():
        # Read the latest telemetry fields inside the repeating loop container
        current_bot_data = db.get_bot_telemetry()
        
        if current_bot_data["route_in_progress"]:
            st.success("🚚 TURBO Rover is Driving Live!")
            
            t1, t2 = st.columns(2)
            t1.metric(label="Current Mission Target Status", value=current_bot_data["status"])
            t2.metric(label="Rover Battery Reserve 🔋", value=f"{current_bot_data['battery']}%")
            
            # Displays a highlighted info block showing coordinate movements
            st.info(f"🛰️ Telemetry Stream Coordinates: Latitude `{current_bot_data['live_lat']:.6f}` | Longitude `{current_bot_data['live_lng']:.6f}`")
            
            # Pro tip: This progress bar will match the admin tracker's position index!
            total_waypoints = 3  # Maximum waypoint configuration limit
            curr_waypoint = current_bot_data["current_stop_index"]
            st.progress(min(1.0, float(curr_waypoint) / total_waypoints), text=f"Delivery Progress Tracked")
        else:
            st.info("System Idle. Once the admin dispatches a route path, live telemetry updates will stream here.")

    # Run our background tracking fragment function
    render_live_user_tracking()


# Catch-all view for incomplete secondary page features
else:
    st.title(f"📋 {st.session_state['page']}")
    st.info("This section layout configuration is ready for custom elements.")
