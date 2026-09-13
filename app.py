import streamlit as st
import pandas as pd
import requests
import os
from backend import (analyze_grievance, save_complaint, get_all_complaints, update_ticket_status, get_ticket_details)

st.set_page_config(page_title="JanSeva AI", layout="wide")
st.title("🇮🇳 JanSeva AI: Public Grievance Redressal")
st.write("Automated AI Triage, GPS Routing & Two-Way Citizen Push Notifications")

tab1, tab2 = st.tabs(["Citizen Lodging Portal", "Ward Officer Dashboard"])

with tab1:
    st.subheader("File a Grievance")
    ward = st.selectbox("Select Your Ward / Zone", ["Zone 1 - Central Headquarters", "Zone 2 - North District", "Zone 3 - South District"])
    complaint_text = st.text_area("Describe your grievance in detail:")
    if st.button("Submit Grievance"):
        if complaint_text:
            with st.spinner("AI is analyzing..."):
                ai_decision = analyze_grievance(complaint_text)
                ticket_id = save_complaint(ward, complaint_text, ai_decision, "", "", 0.0, 0.0)
            st.success(f"Grievance Lodged! Your Ticket ID: {ticket_id}")

with tab2:
    st.subheader("Real-Time Officer Incident Board")
    rows = get_all_complaints()
    if rows:
        df = pd.DataFrame(rows, columns=["Ticket ID", "Logged At", "Ward", "Category", "Department", "Severity", "Summary", "Status"])
        
        def highlight_critical(val):
            return 'background-color: #ff4b4b' if 'CRITICAL' in str(val) else ''
        
        st.dataframe(df.style.map(highlight_critical, subset=['Severity']), use_container_width=True, hide_index=True)
        
        st.divider()
        colA, colB = st.columns(2)
        
        with colA:
            selected_ticket = st.selectbox("Select Ticket to Inspect", df["Ticket ID"].tolist())
            ticket_data = get_ticket_details(selected_ticket)
            
            if ticket_data:
                if ticket_data.get("lat") and ticket_data.get("lng") and ticket_data["lat"] != 0.0:
                    st.write("📍 **Live Incident Map:**")
                    map_df = pd.DataFrame({'lat': [ticket_data['lat']], 'lon': [ticket_data['lng']]})
                    st.map(map_df, zoom=15)
                
                if ticket_data.get("media_path"):
                    st.write("**Attached Citizen Evidence:**")
                    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
                    raw_file_id = ticket_data["media_path"].split('.')[0] 
                    try:
                        req = requests.get(f"https://api.telegram.org/bot{bot_token}/getFile?file_id={raw_file_id}").json()
                        file_path = req["result"]["file_path"]
                        direct_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                        _, ext = os.path.splitext(file_path)
                        if ext.lower() in ['.jpg', '.jpeg', '.png']: st.image(direct_url, width=300)
                        elif ext.lower() in ['.mp4', '.mov']: st.video(direct_url)
                        elif ext.lower() in ['.ogg', '.mp3', '.wav']: st.audio(direct_url)
                        else: st.markdown(f"[**⬇️ Download Evidence**]({direct_url})", unsafe_allow_html=True)
                    except:
                        st.error("Media link unavailable.")

        with colB:
            new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Resolved"])
            if st.button("Apply & Notify Citizen via Telegram"):
                update_ticket_status(selected_ticket, new_status)
                if ticket_data and ticket_data.get("chat_id"):
                    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    msg = f"🔔 *Live Update!*\n🎫 *Ticket ID:* `{selected_ticket}`\n📊 *New Status:* *{new_status}*"
                    requests.post(url, json={"chat_id": ticket_data["chat_id"], "text": msg, "parse_mode": "Markdown"})
                    st.success("Push notification sent to Citizen!")