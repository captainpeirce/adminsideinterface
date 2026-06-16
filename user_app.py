import streamlit as st
import plotly.graph_objects as go
import datetime, random
import pandas as pd
import db_manager as db  # Shared database engine link!

# ── 1. PAGE CONFIGURATION ────────────────────────────────────────────────────
st.set_page_config(
    page_title="NAVIGO — The future of Last-mile logistics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 2. PALETTE CONSTANTS ─────────────────────────────────────────────────────
NAVY    = "#0a2540"
BLUE    = "#4589f5"
TEAL    = "#06b6d4"
PURPLE  = "#8b5cf6"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER  = "#ef4444"

# ── 3. CLEAN GLOBAL UI STYLE RULES (REVERTED TO ORIGINAL PALETTE) ───────────
# ── 3. CLEAN GLOBAL UI STYLE RULES (EXACT CARD REPLICATION) ────────────────
st.markdown(f"""
<style>
/* App Body Background - Clean Light Gradient */
[data-testid="stAppViewContainer"] {{ 
    background: linear-gradient(180deg, #eef4ff 0%, #f8fbff 100%) !important; 
    color: #0a2540 !important;
}}

/* Clear padding safely */
[data-testid="block-container"] {{
    background-color: transparent !important;
    padding-top: 1.4rem !important;
    padding-bottom: 2.5rem !important;
}}

/* Sidebar Design Elements */
[data-testid="stSidebar"] {{ 
    background: linear-gradient(180deg, #071a30 0%, {NAVY} 100%) !important; 
}}
[data-testid="stSidebar"] .stButton > button {{
    width: 100%; background: transparent; border: none; text-align: left;
    padding: 10px 16px; border-radius: 10px; color: #e2e8f0 !important;
    font-size: 14px; transition: all .2s; margin-bottom: 2px;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(69, 137, 245, 0.25) !important;
    color: white !important;
}}

/* FORCE WHITE METRIC AND FEATURE CARDS (This fixes your bug!) */
.metric-card, .feature-box, .step-card, div[data-testid="stForm"] {{
    background-color: #ffffff !important;
    background: #ffffff !important;
    border-radius: 16px !important;
    padding: 22px 18px !important;
    box-shadow: 0 10px 25px rgba(10, 37, 64, 0.05) !important;
    border: 1px solid #e2e8f0 !important;
    color: #1e293b !important;
    display: block !important;
}}

/* Maintain blue top bar accent strictly for feature boxes */
.feature-box {{
    border-top: 4px solid {BLUE} !important;
}}

/* Hero Header Card Container */
.hero-card {{ 
    background: linear-gradient(135deg, #071a30 0%, #0f3460 50%, #1a5276 100%) !important; 
    border-radius: 24px; padding: 36px 32px; color: white !important; margin-bottom: 28px; 
    box-shadow: 0 8px 32px rgba(10,37,64,.25) !important;
    position: relative; overflow: hidden;
}}
.hero-card h1, .hero-card p {{ color: white !important; }}

/* Typography Controls */
h1, h2, h3 {{ 
    color: {NAVY} !important; 
    font-weight: 700 !important; 
}}

/* Form Elements Input Fixes */
.stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {{
    background-color: #ffffff !important;
    color: #0a2540 !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}}
[data-testid="stWidgetLabel"], [data-testid="stRadio"] label p {{
    color: #0a2540 !important;
    font-weight: 600 !important;
}}

/* 🗺️ MAP PROTECTION RULES: Keeps map tiles crisp and perfectly colored */
h1, h2, h3, p, span, label, li:not(.folium-map *) {{
    color: inherit;
}}
.folium-map, .folium-map *, .leaflet-container, .leaflet-container * {{
    color: initial !important;
    background-color: initial !important;
    background: initial !important;
}}
/* 📊 FORCES WHITE BACKGROUND BOX ENCLOSURES ONLY FOR THE HOME PAGE METRIC ROW */
[data-testid="stAppViewContainer"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(4)) > div[data-testid="column"] > div {{
    background-color: #ffffff !important;
    background: #ffffff !important;
    border-radius: 16px !important;
    padding: 22px 18px !important;
    box-shadow: 0 10px 25px rgba(10, 37, 64, 0.06) !important;
    border: 1px solid #e2e8f0 !important;
    text-align: center !important;
}}

/* Ensures clean text alignments inside our specific home page metrics cards */
[data-testid="stAppViewContainer"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(4)) div[data-testid="stMetricValue"], 
[data-testid="stAppViewContainer"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(4)) div[data-testid="stMetricLabel"] {{
    display: flex !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
}}

}}

/* Clean typography fixes to center text alignments inside your new cards */
div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {{
    display: flex !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
}}

</style>
""", unsafe_allow_html=True)


# ── 4. NAVIGATION STATE CONTROL ──────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# ── 5. SIDEBAR LOGO AND APP STATUS DOCK ──────────────────────────────────────
# Sidebar Branding Logo Panel (Fixed to render your beautiful image!)
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)


# Fetch latest telemetry flags to evaluate hardware state updates live
bot_data = db.get_bot_telemetry()
requests_list = db.get_all_requests()

is_active = bot_data["route_in_progress"] or "Returning" in bot_data["status"]
status_badge = "● TURBO Online" if is_active else "● TURBO Idle"
status_color = SUCCESS if is_active else WARNING

st.sidebar.markdown(f"""
<div style='text-align:center; margin-bottom:20px;'>
    <span style='background:rgba(34,197,94,0.15); color:{status_color}; padding:6px 16px; border-radius:20px; font-size:12px; font-weight:700;'>
        {status_badge}
    </span>
</div>
""", unsafe_allow_html=True)

# Sidebar Button Items Mapping Array
if st.sidebar.button("🏠 Home"): st.session_state["page"] = "Home"
if st.sidebar.button("📦 Request Delivery"): st.session_state["page"] = "Request Delivery"
if st.sidebar.button("📍 Live Tracking"): st.session_state["page"] = "Live Tracking"
if st.sidebar.button("🔔 Notifications"): st.session_state["page"] = "Notifications"
if st.sidebar.button("📋 Helpdesk"): st.session_state["page"] = "Helpdesk"
if st.sidebar.button("⭐ Feedback"): st.session_state["page"] = "Feedback"

# Baseline calculation arrays mapping metrics counters data feeds
total_completed_all_time = 284 + len([r for r in requests_list if r["status"] == "Delivered"])
active_deliveries_count = sum(1 for r in requests_list if r["status"] == "Pending" or r["status"] == "In Transit")

# ── 6. DYNAMIC ROUTING VIEWS CHANNELS ────────────────────────────────────────

# PANEL VIEW A: DASHBOARD PORTAL OVERVIEW
if st.session_state["page"] == "Home":
    st.markdown(f"""
    <div class='hero-card'>
        <h1 style='margin:0; font-size:2.4rem;'>Meet TURBO 🚚</h1>
        <p style='margin:12px 0; opacity:0.85; font-size:1.05rem; max-width:600px;'>
            Your Autonomous Campus Delivery Companion — faster, smarter, and fully trackable. Zero waiting. Zero hassle. Pure efficiency.
        </p>
        <div style='display:flex; gap:12px; margin-top:15px;'>
            <span class='badge-success'>● TURBO Online</span>
            <span class='badge-info'>⚡ Avg Delivery: 8 min</span>
            <span class='badge-warning'>📦 284 Deliveries Completed</span>
        </div>
    </div>

    <!-- 📊 REPLICATED METRIC CARDS GRID -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 35px;">
        <div style="background: white; border-radius: 16px; padding: 22px 18px; box-shadow: 0 4px 18px rgba(10,37,64,.06); text-align: center; border: 1px solid #e2e8f0;">
            <div style="color: {BLUE}; font-size: 2.2rem; font-weight: 800; margin-bottom: 4px;">{active_deliveries_count}</div>
            <div style="color: #475569; font-size: 14px; font-weight: 700; margin-bottom: 2px;">Active Deliveries</div>
            <div style="color: #64748b; font-size: 12px; font-weight: 600;">+1 from yesterday</div>
        </div>
        <div style="background: white; border-radius: 16px; padding: 22px 18px; box-shadow: 0 4px 18px rgba(10,37,64,.06); text-align: center; border: 1px solid #e2e8f0;">
            <div style="color: {SUCCESS}; font-size: 2.2rem; font-weight: 800; margin-bottom: 4px;">{total_completed_all_time}</div>
            <div style="color: #475569; font-size: 14px; font-weight: 700; margin-bottom: 2px;">Total Completed</div>
            <div style="color: #64748b; font-size: 12px; font-weight: 600;">All time</div>
        </div>
        <div style="background: white; border-radius: 16px; padding: 22px 18px; box-shadow: 0 4px 18px rgba(10,37,64,.06); text-align: center; border: 1px solid #e2e8f0;">
            <div style="color: {WARNING}; font-size: 2.2rem; font-weight: 800; margin-bottom: 4px;">8 min</div>
            <div style="color: #475569; font-size: 14px; font-weight: 700; margin-bottom: 2px;">Avg Delivery Time</div>
            <div style="color: #64748b; font-size: 12px; font-weight: 600;">-1 min this week</div>
        </div>
        <div style="background: white; border-radius: 16px; padding: 22px 18px; box-shadow: 0 4px 18px rgba(10,37,64,.06); text-align: center; border: 1px solid #e2e8f0;">
            <div style="color: {PURPLE}; font-size: 2.2rem; font-weight: 800; margin-bottom: 4px;">4</div>
            <div style="color: #475569; font-size: 14px; font-weight: 700; margin-bottom: 2px;">TURBO Units</div>
            <div style="color: #64748b; font-size: 12px; font-weight: 600;">3 active · 1 charging</div>
        </div>
    </div>

    <!-- 📌 CORE FEATURES ROW -->
    <h3 style='color:#0a2540; margin-top:20px; margin-bottom:15px;'>📌 Core Features</h3>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 35px;">
        <div class="feature-box"><b>📍 Geo Tracking</b><br><span style='font-size:13px; color:#64748b;'>Real-time live map of TURBO's exact position on campus.</span></div>
        <div class="feature-box"><b>🔒 End-to-End Security</b><br><span style='font-size:13px; color:#64748b;'>Lockable compartment + live camera. Your item, protected.</span></div>
        <div class="feature-box"><b>🔔 Smart Notifications</b><br><span style='font-size:13px; color:#64748b;'>Instant alerts for every delivery milestone automatically.</span></div>
        <div class="feature-box"><b>🛠️ Fleet Maintenance</b><br><span style='font-size:13px; color:#64748b;'>Health dashboard, battery status and issue reporting.</span></div>
    </div>

    <!-- 📦 HOW NAVIGO WORKS SECTION -->
    <h3 style='color:#0a2540; margin-top:20px; margin-bottom:15px;'>📦 How NAVIGO Works</h3>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 35px;">
        <div style="background: white; border-radius: 16px; padding: 24px 18px; text-align: center; box-shadow: 0 4px 16px rgba(10,37,64,.05); border: 1px solid #e2e8f0;">
            <div style="background: #eef4ff; color: {BLUE}; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px auto; font-weight: 700; font-size: 12px;">STEP 1</div>
            <b style="color: #0a2540; display: block; margin-bottom: 6px;">Place Request</b>
            <span style="font-size: 12px; color: #64748b;">Submit via the app in seconds - pick item, location and priority level.</span>
        </div>
        <div style="background: white; border-radius: 16px; padding: 24px 18px; text-align: center; box-shadow: 0 4px 16px rgba(10,37,64,.05); border: 1px solid #e2e8f0;">
            <div style="background: #e6fffa; color: {TEAL}; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px auto; font-weight: 700; font-size: 12px;">STEP 2</div>
            <b style="color: #0a2540; display: block; margin-bottom: 6px;">TURBO Assigned</b>
            <span style="font-size: 12px; color: #64748b;">The nearest available TURBO unit is dispatched to your pickup point.</span>
        </div>
        <div style="background: white; border-radius: 16px; padding: 24px 18px; text-align: center; box-shadow: 0 4px 16px rgba(10,37,64,.05); border: 1px solid #e2e8f0;">
            <div style="background: #f3e8ff; color: {PURPLE}; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px auto; font-weight: 700; font-size: 12px;">STEP 3</div>
            <b style="color: #0a2540; display: block; margin-bottom: 6px;">Live Tracking</b>
            <span style="font-size: 12px; color: #64748b;">Follow TURBO's journey on the live campus map in real-time.</span>
        </div>
        <div style="background: white; border-radius: 16px; padding: 24px 18px; text-align: center; box-shadow: 0 4px 16px rgba(10,37,64,.05); border: 1px solid #e2e8f0;">
            <div style="background: #f0fdf4; color: {SUCCESS}; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px auto; font-weight: 700; font-size: 12px;">STEP 4</div>
            <b style="color: #0a2540; display: block; margin-bottom: 6px;">Delivered</b>
            <span style="font-size: 12px; color: #64748b;">Package reaches your door. Rate your experience and help us improve!</span>
        </div>
    </div>

    <!-- 🌐 DESIGNED FOR SECTION -->
    <h3 style='color:#0a2540; margin-top:20px; margin-bottom:15px;'>🌐 Designed For</h3>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;">
        <div style="background: white; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,.04); border: 1px solid #e2e8f0;">
            <span style="font-size: 24px; display: block; margin-bottom: 6px;">🎓</span>
            <b style="color: #0a2540; font-size: 13px;">Universities</b>
        </div>
        <div style="background: white; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,.04); border: 1px solid #e2e8f0;">
            <span style="font-size: 24px; display: block; margin-bottom: 6px;">🏡</span>
            <b style="color: #0a2540; font-size: 13px;">Gated Communities</b>
        </div>
        <div style="background: white; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,.04); border: 1px solid #e2e8f0;">
            <span style="font-size: 24px; display: block; margin-bottom: 6px;">🏢</span>
            <b style="color: #0a2540; font-size: 13px;">Corporate Parks</b>
        </div>
        <div style="background: white; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,.04); border: 1px solid #e2e8f0;">
            <span style="font-size: 24px; display: block; margin-bottom: 6px;">🌳</span>
            <b style="color: #0a2540; font-size: 13px;">Smart Public Spaces</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Bottom Call-To-Action Button
    if st.button("🔵 Request a Delivery Now →"):
        st.session_state["page"] = "Request Delivery"
        st.rerun()

# PANEL VIEW B: FORM LOGISTICS DEPLOYMENT FIELD DOCK
elif st.session_state["page"] == "Request Delivery":
    st.markdown("<h2>📦 Log New Last-Mile Delivery</h2>", unsafe_allow_html=True)
    
    with st.form("new_delivery_form", clear_on_submit=True):
        name = st.text_input("Recipient Name", placeholder="Type full name...")
        category = st.selectbox("Classification Type", ["Food", "Parcel", "Medical", "Documents"])
        priority = st.radio("Urgency Operational Level", ["Normal", "High", "Critical"], horizontal=True)
        pickup = st.text_input("Origin Hub (Pickup Point)", placeholder="e.g., Central Kitchen")
        dropoff = st.text_input("Destination Point (Drop-off)", placeholder="e.g., Tech Mahindra Block A")
        
        if st.form_submit_button("Deploy Autonomous Agent"):
            if name and pickup and dropoff:
                new_id = f"NAV-{random.randint(1030, 1999)}"
                now_str = datetime.datetime.now().strftime("%I:%M %p")
                
                # Write cleanly directly to the SQLite shared engine system files
                db.add_request(new_id, name, category, pickup, dropoff, priority, "Pending", now_str)
                st.success(f"🚀 Sent request **{new_id}** to database queue!")
            else:
                st.error("⚠️ Incomplete Fields: Please supply variables for Name, Pickup, and Drop-off points.")

## PANEL VIEW C: MAP AND TELEMETRY REAL-TIME PROGRESS TRACKER (FIXED)
elif st.session_state["page"] == "Live Tracking":
    import folium
    from streamlit_folium import st_folium

    st.markdown("<h2>📍 Real-Time Location Tracker</h2>", unsafe_allow_html=True)
    
    # 🔄 LIVE AUTO-REFRESH WRAPPER CONTAINER (Polls DB directly every 3 seconds)
    @st.fragment(run_every=3)
    def render_live_user_tracking():
        # Re-fetch telemetry fresh on every loop pass step inside the fragment
        current_bot = db.get_bot_telemetry()
        delivery_stops = db.get_waypoints()
        
        if current_bot["route_in_progress"] or "Returning" in current_bot["status"]:
            st.success("🚚 TURBO Rover is Navigating Campus Live!")
            
            t1, t2 = st.columns(2)
            t1.metric(label="Current Mission Target Status", value=current_bot["status"])
            t2.metric(label="Rover Battery Reserve 🔋", value=f"{current_bot['battery']}%")
            
            st.markdown("### 🗺️ Live Delivery Journey Tracker")
            
            # SAFE MAP INJECTION: Check if coordinates exist before drawing map elements
            try:
                bot_lat = current_bot.get("live_lat", 17.570514)
                bot_lng = current_bot.get("live_lng", 78.432775)
                
                # Check for invalid or missing coordinate data structures
                if bot_lat is None or bot_lng is None:
                    bot_lat, bot_lng = 17.570514, 78.432775

                user_map = folium.Map(location=[bot_lat, bot_lng], zoom_start=18)
                
                # Place purple tracking marker for the active bot asset
                folium.Marker(
                    location=[bot_lat, bot_lng],
                    popup=f"Status: {current_bot['status']}",
                    icon=folium.Icon(color="purple", icon="play", prefix="fa")
                ).add_to(user_map)
                
                # Map out flag stops targeting mapped waypoints coordinate pins
                if delivery_stops:
                    for idx, stop in enumerate(delivery_stops):
                        # Add a safety check to ensure individual stops have valid elements
                        if isinstance(stop, (list, tuple)) and len(stop) >= 2:
                            flag_color = "gray" if idx < current_bot["current_stop_index"] else \
                                         ("orange" if idx == current_bot["current_stop_index"] else "red")
                            folium.Marker(location=[stop[0], stop[1]], icon=folium.Icon(color=flag_color, icon="flag")).add_to(user_map)
                    
                    # Wire structural linear connection traces along the route map values path
                    path_lines = [[bot_lat, bot_lng]] + [[s[0], s[1]] for s in delivery_stops if isinstance(s, (list, tuple)) and len(s) >= 2]
                    folium.PolyLine(locations=path_lines, color="#4589f5", weight=4, dash_array="6, 6").add_to(user_map)
                    
                st_folium(user_map, height=440, width="100%", key="user_live_delivery_tracking_map")
                st.info(f"🛰️ Coordinate Stream: Latitude `{bot_lat:.6f}` | Longitude `{bot_lng:.6f}`")
                
            except Exception as e:
                st.warning("🔄 Syncing map telemetry stream...")
        else:
            st.info("System Idle. Once the admin dispatches a route path, live telemetry updates will stream here.")

    # Execute polling data fragment
    render_live_user_tracking()
