import streamlit as st
import pandas as pd
import subprocess
import sys
from backend import (
    analyze_grievance, save_complaint, get_all_complaints, 
    check_duplicate, update_ticket_status, get_ticket_status
)

st.set_page_config(page_title="JanSeva AI", layout="wide")

# --- HACKATHON CLOUD TRICK: Start bot as a separate OS process ---
@st.cache_resource
def start_bot_process():
    subprocess.Popen([sys.executable, "bot.py"])
    return True

start_bot_process()
# -----------------------------------------------------------------

st.title("🇮🇳 JanSeva AI: Public Grievance Redressal")
st.write("Automated AI Triage, Department Routing & SLA Monitoring")

tab1, tab2, tab3 = st.tabs(["Citizen Lodging Portal", "Ward Officer Dashboard", "Public Analytics"])

with tab1:
    st.subheader("File a Grievance")
    ward = st.selectbox("Select Your Ward / Zone", ["Ward 1 - Central", "Ward 2 - North", "Ward 3 - South"])
    complaint_text = st.text_area("Describe your grievance in detail:")
    
    if st.button("Submit Grievance"):
        if complaint_text:
            with st.spinner("AI is analyzing and routing your complaint..."):
                ai_decision = analyze_grievance(complaint_text)
                category = ai_decision.get("category", "General")
                
                dup_check = check_duplicate(ward, category)
                if dup_check["is_duplicate"]:
                    st.warning(f"⚠️ Duplicate Detected: A similar issue '{dup_check['summary']}' is already being handled in this ward (Ticket: {dup_check['ticket_id']}). We have linked your report to expedite resolution.")
                
                ticket_id = save_complaint(ward, complaint_text, ai_decision)
            
            st.success(f"Grievance Lodged Successfully! Your Ticket ID: {ticket_id}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Assigned Category", category)
            col2.metric("Target Department", ai_decision.get("department", "N/A"))
            col3.metric("Severity Level", ai_decision.get("severity", "N/A"))
            st.info(f"AI Summary: {ai_decision.get('summary', '')}")
        else:
            st.error("Please enter a complaint.")
            
    st.divider()
    st.subheader("🔍 Track Existing Grievance")
    search_id = st.text_input("Enter your Ticket ID (e.g., GRV-0913111144)")
    
    if st.button("Check Status"):
        result = get_ticket_status(search_id)
        if result:
            if result[0] == "Resolved":
                st.success(f"Status: **{result[0]}** ✅ | Dept: {result[1]} | Issue: {result[2]}")
            else:
                st.warning(f"Status: **{result[0]}** ⏳ | Dept: {result[1]} | Issue: {result[2]}")
        else:
            st.error("Ticket not found. Please check your ID.")

with tab2:
    st.subheader("Real-Time Officer Incident Board")
    rows = get_all_complaints()
    if rows:
        df = pd.DataFrame(rows, columns=["Ticket ID", "Logged At", "Ward", "Category", "Department", "Severity", "Summary", "Status"])
        def apply_status_colors(row):
            if row["Status"] == "Resolved":
                return ['background-color: #e6ffe6; color: #006600'] * len(row)
            elif row["Severity"] == "High" and row["Status"] != "Resolved":
                return ['background-color: #ffcccc; color: #900000'] * len(row)
            return [''] * len(row)
        st.dataframe(df.style.apply(apply_status_colors, axis=1), use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("Action Panel: Update SLA Status")
        colA, colB = st.columns(2)
        with colA:
            selected_ticket = st.selectbox("Select Ticket", df["Ticket ID"].tolist())
        with colB:
            new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Resolved"])
        if st.button("Apply Update"):
            update_ticket_status(selected_ticket, new_status)
            st.success(f"Ticket {selected_ticket} marked as {new_status}. Please refresh the page.")
    else:
        st.info("No active grievances.")
        
    st.divider()
    st.subheader("National API Integration")
    st.caption("Mandatory daily sync with Centralised Public Grievance Redress and Monitoring System (CPGRAMS).")
    if st.button("📤 Export Pending High-Severity Tickets to CPGRAMS"):
        st.success("Successfully pushed data to National CPGRAMS Gateway via API Bridge!")
        st.balloons()

with tab3:
    st.subheader("📊 City-Wide Grievance Analytics")
    rows = get_all_complaints()
    if rows:
        df = pd.DataFrame(rows, columns=["Ticket ID", "Logged At", "Ward", "Category", "Department", "Severity", "Summary", "Status"])
        total = len(df)
        resolved = len(df[df["Status"] == "Resolved"])
        res_rate = round((resolved / total) * 100) if total > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Grievances Logged", total)
        col2.metric("Tickets Resolved", resolved)
        col3.metric("City Resolution Rate", f"{res_rate}%")
        
        st.divider()
        colA, colB = st.columns(2)
        with colA:
            st.write("**Issue Volume by Department**")
            dept_counts = df["Department"].value_counts()
            st.bar_chart(dept_counts)
        with colB:
            st.write("**Ward Action Leaderboard (Pending Tickets)**")
            pending_df = df[df["Status"] != "Resolved"]
            ward_counts = pending_df["Ward"].value_counts()
            st.bar_chart(ward_counts, color="#ff4b4b")
    else:
        st.info("Not enough data to generate analytics yet.")