import sqlite3

DB_FILE = "navigo_system.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY, name TEXT, category TEXT, 
            pickup TEXT, dropoff TEXT, priority TEXT, status TEXT, ts TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_telemetry (
            id TEXT PRIMARY KEY, live_lat REAL, live_lng REAL, 
            status TEXT, battery TEXT, current_stop_index INTEGER, route_in_progress INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS waypoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT, lat REAL, lng REAL
        )
    ''')
    c.execute("SELECT COUNT(*) FROM bot_telemetry")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO bot_telemetry VALUES ('BOT-01', 17.570514, 78.432775, '🔴 Offline / Idle', '100', 0, 0)")
    conn.commit()
    conn.close()

def get_all_requests():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM requests ORDER BY ts DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def add_request(req_id, name, cat, pickup, dropoff, priority, status, ts):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO requests VALUES (?,?,?,?,?,?,?,?)", (req_id, name, cat, pickup, dropoff, priority, status, ts))
    conn.commit()
    conn.close()

def get_bot_telemetry():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT live_lat, live_lng, status, battery, current_stop_index, route_in_progress FROM bot_telemetry WHERE id='BOT-01'")
    row = c.fetchone()
    conn.close()
    return {
        "live_lat": row[0], "live_lng": row[1], "status": row[2],
        "battery": row[3], "current_stop_index": row[4], "route_in_progress": bool(row[5])
    }

def update_bot_telemetry(lat, lng, status, battery, stop_idx, in_progress):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        UPDATE bot_telemetry 
        SET live_lat=?, live_lng=?, status=?, battery=?, current_stop_index=?, route_in_progress=? 
        WHERE id='BOT-01'
    ''', (lat, lng, status, battery, stop_idx, int(in_progress)))
    conn.commit()
    conn.close()

def get_waypoints():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT lat, lng FROM waypoints ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_waypoint(lat, lng):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO waypoints (lat, lng) VALUES (?,?)", (lat, lng))
    conn.commit()
    conn.close()

def clear_waypoints():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM waypoints")
    conn.commit()
    conn.close()

init_db()
def clear_all_requests():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM requests")
    conn.commit()
    conn.close()
