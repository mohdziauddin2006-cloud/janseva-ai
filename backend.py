import os
import json
import math
import psycopg2
from datetime import datetime
from google import genai

DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    # 1. Create the base table if it doesn't exist at all
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grievances (
            id TEXT PRIMARY KEY,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            chat_id TEXT,
            user_name TEXT,
            raw_text TEXT,
            media_type TEXT,
            media_file_id TEXT,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            ward TEXT,
            category TEXT,
            department TEXT,
            severity TEXT,
            summary TEXT,
            status TEXT DEFAULT 'Pending'
        );
    """)
    conn.commit()
    
    # 2. Safely force Postgres to upgrade the old table with any missing columns
    cur.execute("ALTER TABLE grievances ADD COLUMN IF NOT EXISTS user_name TEXT;")
    cur.execute("ALTER TABLE grievances ADD COLUMN IF NOT EXISTS chat_id TEXT;")
    cur.execute("ALTER TABLE grievances ADD COLUMN IF NOT EXISTS media_type TEXT;")
    cur.execute("ALTER TABLE grievances ADD COLUMN IF NOT EXISTS media_file_id TEXT;")
    cur.execute("ALTER TABLE grievances ADD COLUMN IF NOT EXISTS raw_text TEXT;")
    conn.commit()
    
    cur.close()
    conn.close()

def analyze_grievance(text):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    Analyze this public grievance text: "{text}"
    Return ONLY a valid JSON object with keys:
    - "category": [Water Supply, Sanitation, Roads, Electricity, Public Health]
    - "department": [Water Board, Solid Waste, Public Works, Power Bureau, Health Dept]
    - "severity": "High" | "Medium" | "Low"
    - "summary": 1 concise sentence summary
    """
    try:
        res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        clean = res.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {"category": "General", "department": "Civic Body", "severity": "Medium", "summary": text[:80] if text else "Media attached"}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def check_50m_density(lat, lon):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT lat, lon FROM grievances WHERE status != 'Resolved' AND lat IS NOT NULL AND lon IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    cluster_count = sum(1 for r_lat, r_lon in rows if haversine(lat, lon, r_lat, r_lon) <= 50)
    return "🔥 CRITICAL" if cluster_count >= 3 else None

def save_grievance(chat_id, user_name, raw_text, media_type, media_file_id, lat, lon):
    init_db()
    ai_data = analyze_grievance(raw_text if raw_text else "Media file uploaded")
    
    density_sev = check_50m_density(lat, lon) if lat and lon else None
    final_sev = density_sev if density_sev else ai_data.get("severity", "Medium")
    
    ticket_id = f"GRV-{datetime.now().strftime('%m%d%H%M%S')}"
    ward = "Ward 1 - Central" 
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO grievances (id, chat_id, user_name, raw_text, media_type, media_file_id, lat, lon, ward, category, department, severity, summary, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
    """, (ticket_id, str(chat_id), user_name, raw_text, media_type, media_file_id, lat, lon, ward, ai_data.get("category"), ai_data.get("department"), final_sev, ai_data.get("summary")))
    conn.commit()
    cur.close()
    conn.close()
    
    return {"ticket_id": ticket_id, "category": ai_data.get("category"), "severity": final_sev, "summary": ai_data.get("summary")}

def get_all_complaints():
    init_db()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, timestamp::date, user_name, category, department, status, severity, summary, lat, lon, media_type, media_file_id, raw_text FROM grievances ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows