import os
import psycopg2
import json
import math
from datetime import datetime
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
DB_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DB_URL)

def init_db():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grievances (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                ward TEXT,
                raw_text TEXT,
                category TEXT,
                department TEXT,
                severity TEXT,
                summary TEXT,
                status TEXT,
                chat_id TEXT,
                media_path TEXT,
                lat REAL,
                lng REAL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Init Error:", e)

def get_nearest_office(lat, lng):
    offices = {
        "Zone 1 - Central Headquarters": (17.3850, 78.4867),
        "Zone 2 - North District": (17.4400, 78.4700),
        "Zone 3 - South District": (17.3600, 78.4700)
    }
    closest_ward = "Zone 1 - Central Headquarters"
    min_dist = float('inf')
    for ward, coords in offices.items():
        dist = math.hypot(lat - coords[0], lng - coords[1])
        if dist < min_dist:
            min_dist = dist
            closest_ward = ward
    return closest_ward

def check_density(lat, lng, current_severity):
    if lat == 0.0 or lng == 0.0:
        return current_severity
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT lat, lng FROM grievances WHERE status != 'Resolved'")
        rows = cursor.fetchall()
        conn.close()
        
        nearby_count = 0
        R = 6371000 # Earth radius
        for row in rows:
            r_lat, r_lng = row[0], row[1]
            if r_lat == 0.0 or r_lng == 0.0: continue
            
            phi1, phi2 = math.radians(lat), math.radians(r_lat)
            dphi = math.radians(r_lat - lat)
            dlng = math.radians(r_lng - lng)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlng/2)**2
            dist = R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))
            
            if dist <= 50:
                nearby_count += 1
                
        if nearby_count >= 3:
            return "🔥 CRITICAL (High Density: 3+ reports within 50m)"
        return current_severity
    except:
        return current_severity

def analyze_grievance(complaint_text):
    client = genai.Client(api_key=API_KEY)
    prompt = f"""
    You are an expert government grievance triage system. Analyze the following citizen complaint and categorize it.
    Return ONLY a valid JSON object with no markdown.
    Strictly choose the "category" from: [Water Supply, Sanitation & Waste, Roads & Traffic, Electricity]
    Strictly choose the "department" from: [Water Board, Solid Waste Management, Public Works Dept, Power Bureau]
    Required keys: "category", "department", "severity" (High, Medium, Low), "summary" (One sentence summary)
    Complaint: {complaint_text}
    """
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception:
        return {"category": "General", "department": "Public Grievance Cell", "severity": "Medium", "summary": complaint_text[:80]}

def save_complaint(ward, complaint_text, ai_data, chat_id="", media_path="", lat=0.0, lng=0.0):
    init_db()
    final_severity = check_density(lat, lng, ai_data.get("severity", "Medium"))
    conn = get_conn()
    cursor = conn.cursor()
    ticket_id = f"GRV-{datetime.now().strftime('%m%d%H%M%S')}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    cursor.execute('''
        INSERT INTO grievances (id, timestamp, ward, raw_text, category, department, severity, summary, status, chat_id, media_path, lat, lng)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (ticket_id, timestamp, ward, complaint_text, ai_data.get("category", "General"), ai_data.get("department", "Civic Body"), final_severity, ai_data.get("summary", ""), "Pending", chat_id, media_path, lat, lng))
    conn.commit()
    conn.close()
    return ticket_id

def get_all_complaints():
    init_db()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, ward, category, department, severity, summary, status FROM grievances ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_ticket_details(ticket_id):
    init_db()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM grievances WHERE id=%s", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "status": row[8], "chat_id": row[9], "media_path": row[10], "lat": row[11], "lng": row[12]}
    return None

def update_ticket_status(ticket_id, new_status):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE grievances SET status=%s WHERE id=%s", (new_status, ticket_id))
    conn.commit()
    conn.close()