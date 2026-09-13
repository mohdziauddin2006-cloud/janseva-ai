import streamlit as st
import pandas as pd
import plotly.express as px
from backend import get_all_complaints

st.set_page_config(page_title="JanSeva AI - Admin Dashboard", layout="wide")

# Custom CSS to mimic the clean Figma UI (Cards, Shadows, White Backgrounds)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .kpi-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid;
    }
    .total { border-color: #6c757d; }
    .pending { border-color: #f59e0b; }
    .review { border-color: #3b82f6; }
    .resolved { border-color: #10b981; }
    .critical { border-color: #ef4444; }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=80)
    st.title("JanSeva AI")
    st.caption("Municipal Command Center")
    st.divider()
    page = st.radio("Navigation", ["📊 Overview", "📍 Spatial Incident Map", "📋 All Grievances"])

# Fetch Data
rows = get_all_complaints()
cols = ["ID", "Date", "Citizen", "Category", "Department", "Status", "Priority", "Summary", "Lat", "Lon"]
df = pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)

if page == "📊 Overview":
    st.title("Admin Dashboard")
    st.caption("Grievance Management — State Municipal Corporation")
    
    # KPI Row (Mimicking the Figma Cards)
    if not df.empty:
        total = len(df)
        pending = len(df[df["Status"] == "Pending"])
        review = len(df[df["Status"] == "In Progress"])
        resolved = len(df[df["Status"] == "Resolved"])
        critical = len(df[df["Priority"].str.contains("CRITICAL") | df["Priority"].str.contains("High")])
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(f'<div class="kpi-card total">📄 <b>Total</b><br><h2 style="margin:0;">{total}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card pending">🕒 <b>Pending</b><br><h2 style="margin:0; color:#f59e0b;">{pending}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-card review">👁️ <b>In Review</b><br><h2 style="margin:0; color:#3b82f6;">{review}</h2></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-card resolved">✅ <b>Resolved</b><br><h2 style="margin:0; color:#10b981;">{resolved}</h2></div>', unsafe_allow_html=True)
        c5.markdown(f'<div class="kpi-card critical">🚨 <b>Critical</b><br><h2 style="margin:0; color:#ef4444;">{critical}</h2></div>', unsafe_allow_html=True)
        
        st.write("---")
        
        # Charts Row
        col_chart1, col_chart2 = st.columns([1.5, 1])
        
        with col_chart1:
            st.subheader("Grievances by Category")
            bar_data = df["Category"].value_counts().reset_index()
            bar_data.columns = ["Category", "Count"]
            fig_bar = px.bar(bar_data, x="Category", y="Count", color_discrete_sequence=["#7f1d1d"])
            fig_bar.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_chart2:
            st.subheader("Status Distribution")
            pie_data = df["Status"].value_counts().reset_index()
            pie_data.columns = ["Status", "Count"]
            color_map = {"Resolved": "#10b981", "Pending": "#f59e0b", "In Progress": "#3b82f6"}
            fig_pie = px.pie(pie_data, values="Count", names="Status", hole=0.4, color="Status", color_discrete_map=color_map)
            fig_pie.update_layout(margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data available.")

elif page == "📍 Spatial Incident Map":
    st.title("Live Density Escalation Map")
    st.caption("Visualizing 50-meter critical clustering algorithms in real-time.")
    if not df.empty and not df['Lat'].isnull().all():
        map_df = df.dropna(subset=['Lat', 'Lon'])
        map_df = map_df.rename(columns={"Lat": "latitude", "Lon": "longitude"})
        st.map(map_df)
    else:
        st.warning("No valid GPS coordinates logged yet.")

elif page == "📋 All Grievances":
    st.title("All Grievances")
    
    # Clean Dataframe styling
    def color_status(val):
        color = '#10b981' if val == 'Resolved' else '#f59e0b' if val == 'Pending' else '#3b82f6' if val == 'In Progress' else 'black'
        return f'color: {color}; font-weight: bold;'
        
    def color_priority(val):
        color = '#ef4444' if 'CRITICAL' in str(val) or 'High' in str(val) else '#f59e0b' if 'Medium' in str(val) else 'gray'
        return f'color: {color}; font-weight: bold;'

    if not df.empty:
        display_df = df[["ID", "Citizen", "Summary", "Category", "Status", "Priority", "Date"]]
        styled_df = display_df.style.map(color_status, subset=['Status']).map(color_priority, subset=['Priority'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)
    else:
        st.info("No grievances found.")