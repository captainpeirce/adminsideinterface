import streamlit as st
import psycopg2
import psycopg2.extras

# Pull the shared internet URL from Streamlit Cloud Secrets safely
DB_URL = st.secrets["DATABASE_URL"]

def get_connection():
    """Establishes an active pipeline to your online cloud database."""
    return psycopg2.connect(DB_URL)

def init_db():
    """Creates the data tables inside the cloud network if they don't exist."""
    conn = get_connection()
    c = conn.cursor()
    
    # Table for user delivery requests
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            pickup TEXT,
            dropoff TEXT,
            priority TEXT,
            status TEXT,
            ts TEXT
        )
    ''')
    
    # Table for live robot hardware telemetry
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_telemetry (
            id TEXT PRIMARY KEY,
            live_lat REAL,
            live_lng REAL,
            status TEXT,
            battery TEXT,
            current_stop_index INTEGER,
            route_in_progress INTEGER
        )
    ''')
    
    # Table for mapped geographic waypoints
    c.execute('''
        CREATE TABLE IF NOT EXISTS waypoints (
            id SERIAL PRIMARY KEY,
            lat REAL,
            lng REAL
        )
    ''')
    
    # Insert default bot entry if completely empty
    c.execute("SELECT COUNT(*) FROM bot_telemetry")
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO bot_telemetry VALUES 
            ('BOT-01', 17.570514, 78.432775, '🔴 Offline / Idle', '100', 0, 0)
        ''')
        
    conn.commit()
    conn.close()

# --- REQUESTS API PIPELINES ---
def get_all_requests():
    conn = get_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT * FROM requests ORDER BY ts DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def add_request(req_id, name, cat, pickup, dropoff, priority, status, ts):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO requests VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (req_id, name, cat, pickup, dropoff, priority, status, ts))
    conn.commit()
    conn.close()

def clear_all_requests():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM requests")
    conn.commit()
    conn.close()

# --- TELEMETRY API PIPELINES ---
def get_bot_telemetry():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT live_lat, live_lng, status, battery, current_stop_index, route_in_progress FROM bot_telemetry WHERE id='BOT-01'")
    row = c.fetchone()
    conn.close()
    return {
        "live_lat": row[0], "live_lng": row[1], "status": row[2],
        "battery": row[3], "current_stop_index": row[4], "route_in_progress": bool(row[5])
    }

def update_bot_telemetry(lat, lng, status, battery, stop_idx, in_progress):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE bot_telemetry 
        SET live_lat=%s, live_lng=%s, status=%s, battery=%s, current_stop_index=%s, route_in_progress=%s 
        WHERE id='BOT-01'
    ''', (lat, lng, status, battery, stop_idx, int(in_progress)))
    conn.commit()
    conn.close()

# --- WAYPOINTS API PIPELINES ---
def get_waypoints():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT lat, lng FROM waypoints ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_waypoint(lat, lng):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO waypoints (lat, lng) VALUES (%s,%s)", (lat, lng))
    conn.commit()
    conn.close()

def clear_waypoints():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM waypoints")
    conn.commit()
    conn.close()

def set_return_to_hub_route(start_lat=17.570514, start_lng=78.432775):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM waypoints")
    c.execute("INSERT INTO waypoints (lat, lng) VALUES (%s,%s)", (start_lat, start_lng))
    conn.commit()
    conn.close()

# Run initialization sequence
init_db()
