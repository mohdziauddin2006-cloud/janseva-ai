import os
import sqlite3
import json
from datetime import datetime
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
DB_NAME = "grievances.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
            media_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def analyze_grievance(complaint_text):
    client = genai.Client(api_key=API_KEY)
    prompt = f"""
    You are an expert government grievance triage system. Analyze the following citizen complaint and categorize it.
    Return ONLY a valid JSON object with no markdown.
    Strictly choose the "category" from: [Water Supply, Sanitation & Waste, Roads & Traffic, Electricity, Animal Control, Public Health]
    Strictly choose the "department" from: [Water Board, Solid Waste Management, Public Works Dept, Power Bureau, Municipal Animal Services, Health Dept]
    Required keys: "category", "department", "severity" (High, Medium, Low), "summary" (One sentence summary)
    Complaint: {complaint_text}
    """
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return {"category": "General", "department": "Public Grievance Cell", "severity": "Medium", "summary": complaint_text[:80]}

def check_duplicate(ward, category):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, summary FROM grievances WHERE ward=? AND category=? AND status!='Resolved'", (ward, category))
    match = cursor.fetchone()
    conn.close()
    if match:
        return {"is_duplicate": True, "ticket_id": match[0], "summary": match[1]}
    return {"is_duplicate": False}

def save_complaint(ward, complaint_text, ai_data, chat_id="", media_path=""):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    ticket_id = f"GRV-{datetime.now().strftime('%m%d%H%M%S')}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    cursor.execute('''
        INSERT INTO grievances (id, timestamp, ward, raw_text, category, department, severity, summary, status, chat_id, media_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ticket_id, timestamp, ward, complaint_text, ai_data.get("category", "General"), ai_data.get("department", "Civic Body"), ai_data.get("severity", "Medium"), ai_data.get("summary", ""), "Pending", chat_id, media_path))
    conn.commit()
    conn.close()
    return ticket_id

def get_all_complaints():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, ward, category, department, severity, summary, status FROM grievances ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_ticket_details(ticket_id):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM grievances WHERE id=?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "status": row[8], "chat_id": row[9], "media_path": row[10]
        }
    return None

def update_ticket_status(ticket_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE grievances SET status=? WHERE id=?", (new_status, ticket_id))
    conn.commit()
    conn.close()

def get_ticket_status(ticket_id):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT status, department, summary FROM grievances WHERE id=?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return row