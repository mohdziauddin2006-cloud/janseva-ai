import streamlit as st
import pandas as pd
import requests
import os
from backend import (
    analyze_grievance, save_complaint, get_all_complaints, 
    check_duplicate, update_ticket_status, get_ticket_status, get_ticket_details
)

st.set_page_config(page_title="JanSeva AI", layout="wide")
st.title("🇮🇳 JanSeva AI: Public Grievance Redressal")
st.write("Automated AI Triage & Two-Way Citizen Push Notifications")

tab1, tab2, tab3 = st.tabs(["Citizen Lodging Portal", "Ward Officer Dashboard", "Public Analytics"])

with tab1:
    st.subheader("File a Grievance")
    ward = st.selectbox("Select Your Ward / Zone", ["Ward 1 - Central", "Ward 2 - North", "Ward 3 - South"])
    complaint_text = st.text_area("Describe your grievance in detail:")
    
    if st.button("Submit Grievance"):
        if complaint_text:
            with st.spinner("AI is analyzing..."):
                ai_decision = analyze_grievance(complaint_text)
                ticket_id = save_complaint(ward, complaint_text, ai_decision)
            st.success(f"Grievance Lodged! Your Ticket ID: {ticket_id}")
        else:
            st.error("Please enter a complaint.")

with tab2:
    st.subheader("Real-Time Officer Incident Board")
    rows = get_all_complaints()
    if rows:
        df = pd.DataFrame(rows, columns=["Ticket ID", "Logged At", "Ward", "Category", "Department", "Severity", "Summary", "Status"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("Ticket Inspection & Action Panel")
        colA, colB = st.columns(2)
        
        with colA:
            selected_ticket = st.selectbox("Select Ticket to Inspect", df["Ticket ID"].tolist())
            ticket_data = get_ticket_details(selected_ticket)
            
            # Media Viewer
            if ticket_data and ticket_data["media_path"] and os.path.exists(ticket_data["media_path"]):
                st.write("**Attached Citizen Evidence:**")
                media = ticket_data["media_path"]
                if media.endswith(".jpg"):
                    st.image(media, width=300)
                elif media.endswith(".mp4"):
                    st.video(media)
                elif media.endswith(".ogg"):
                    st.audio(media)
            else:
                st.info("No media attached to this ticket.")

        with colB:
            new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Resolved"])
            if st.button("Apply & Notify Citizen via Telegram"):
                update_ticket_status(selected_ticket, new_status)
                
                # Push Notification Logic
                if ticket_data and ticket_data["chat_id"]:
                    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    msg = f"🔔 *Live Update from Ward Officer!*\n\n🎫 *Ticket ID:* `{selected_ticket}`\n📊 *New Status:* *{new_status}*\n\nYour civic team is working on it."
                    requests.post(url, json={"chat_id": ticket_data["chat_id"], "text": msg, "parse_mode": "Markdown"})
                    st.success(f"Status updated and push notification sent directly to Citizen's phone!")
                    st.balloons()
                else:
                    st.warning("Status updated. (User submitted via web, no Telegram push available).")
    else:
        st.info("No active grievances.")

with tab3:
    st.subheader("📊 City-Wide Grievance Analytics")
    st.info("Data visualizations will populate here as tickets enter the system.")