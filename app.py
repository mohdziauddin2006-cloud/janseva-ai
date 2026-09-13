import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from backend import get_all_complaints

st.set_page_config(page_title="JanSeva AI - Admin Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .kpi-card {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid;
    }
    .total { border-color: #6c757d; } .pending { border-color: #f59e0b; }
    .review { border-color: #3b82f6; } .resolved { border-color: #10b981; }
    .critical { border-color: #ef4444; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=80)
    st.title("JanSeva AI")
    st.caption("Municipal Command Center")
    st.divider()
    page = st.radio("Navigation", ["📊 Overview", "📍 Spatial Incident Map", "📋 All Grievances"])

rows = get_all_complaints()
cols = ["ID", "Date", "Citizen", "Category", "Department", "Status", "Priority", "Summary", "Lat", "Lon", "Media Type", "Media ID", "Raw Text"]
df = pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)

if page == "📊 Overview":
    st.title("Admin Dashboard")
    st.caption("Grievance Management — State Municipal Corporation")
    if not df.empty:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(f'<div class="kpi-card total">📄 Total<br><h2 style="margin:0;">{len(df)}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card pending">🕒 Pending<br><h2 style="margin:0; color:#f59e0b;">{len(df[df["Status"]=="Pending"])}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-card resolved">✅ Resolved<br><h2 style="margin:0; color:#10b981;">{len(df[df["Status"]=="Resolved"])}</h2></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-card critical">🚨 Critical<br><h2 style="margin:0; color:#ef4444;">{len(df[df["Priority"].str.contains("CRITICAL") | df["Priority"].str.contains("High")])}</h2></div>', unsafe_allow_html=True)
        
        st.write("---")
        col_chart1, col_chart2 = st.columns([1.5, 1])
        with col_chart1:
            st.subheader("Grievances by Category")
            bar_data = df["Category"].value_counts().reset_index()
            fig_bar = px.bar(bar_data, x="Category", y="count", color_discrete_sequence=["#7f1d1d"])
            fig_bar.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_chart2:
            st.subheader("Status Distribution")
            pie_data = df["Status"].value_counts().reset_index()
            color_map = {"Resolved": "#10b981", "Pending": "#f59e0b", "In Progress": "#3b82f6"}
            fig_pie = px.pie(pie_data, values="count", names="Status", hole=0.4, color="Status", color_discrete_map=color_map)
            fig_pie.update_layout(margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)

elif page == "📍 Spatial Incident Map":
    st.title("Live Density Escalation Map")
    if not df.empty and not df['Lat'].isnull().all():
        map_df = df.dropna(subset=['Lat', 'Lon']).rename(columns={"Lat": "latitude", "Lon": "longitude"})
        st.map(map_df)

elif page == "📋 All Grievances":
    st.title("All Grievances & Evidence Review")
    
    def color_status(val):
        return f'color: {"#10b981" if val=="Resolved" else "#f59e0b" if val=="Pending" else "black"}; font-weight: bold;'
    def color_priority(val):
        return f'color: {"#ef4444" if "CRITICAL" in str(val) else "#f59e0b" if "Medium" in str(val) else "gray"}; font-weight: bold;'

    if not df.empty:
        display_df = df[["ID", "Citizen", "Summary", "Category", "Status", "Priority", "Date"]]
        st.dataframe(display_df.style.map(color_status, subset=['Status']).map(color_priority, subset=['Priority']), use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("🔍 Inspect Citizen Evidence")
        inspect_id = st.selectbox("Select Ticket ID to view uploaded files:", df["ID"])
        
        if inspect_id:
            row = df[df["ID"] == inspect_id].iloc[0]
            st.write(f"**Original Report Text:** {row['Raw Text']}")
            
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            m_type, m_fid = row["Media Type"], row["Media ID"]
            
            if pd.notna(m_fid) and token:
                try:
                    f_res = requests.get(f"https://api.telegram.org/bot{token}/getFile?file_id={m_fid}").json()
                    if f_res.get("ok"):
                        dl_url = f"https://api.telegram.org/file/bot{token}/{f_res['result']['file_path']}"
                        st.write(f"**Attached Media ({m_type.upper()}):**")
                        if m_type == "photo": st.image(dl_url, width=400)
                        elif m_type == "video": st.video(dl_url)
                        elif m_type in ["audio", "voice"]: st.audio(dl_url)
                        else: st.markdown(f"[Download {m_type} File]({dl_url})")
                except:
                    st.warning("Could not fetch media from Telegram Cloud.")
            else:
                st.info("No media attached to this ticket.")