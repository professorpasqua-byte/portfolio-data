import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration & Theme setup
st.set_page_config(page_title="Meridian Works Workforce Insights", layout="wide", initial_sidebar_state="expanded")

# Force clean dark styling accents
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #38bdf8; font-size: 2.2rem; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #9ca3af; font-size: 1rem; }
    </style>
""", unsafe_allow_html=True)  # FIX: was unsafe_allow_index (not a real parameter), crashed the app

st.title("Meridian Works: Workforce Analytics Hub")
st.caption("Strategic descriptive analytics pipeline exploring employee retention and engagement baseline metrics.")

# 2. Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv(
        "project-1-people-analytics/meridian_works_clean.csv",
        dtype={"Attrition": "string"},   # FIX: force Attrition to stay text, never let it get read as bool
    )
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: 'meridian_works_clean.csv' not found inside project-1-people-analytics folder!")
    st.stop()

# 3. Sidebar Filtering
st.sidebar.header("Analytics Filters")
dept_filter = st.sidebar.selectbox("Select Target Department", ["All Departments"] + sorted(df["Department"].dropna().unique()))

filtered_df = df if dept_filter == "All Departments" else df[df["Department"] == dept_filter]

# 4. Dynamic KPI Metric Grid
st.subheader("Executive Summary KPIs")

is_yes = filtered_df["Attrition"].astype(str).str.strip().str.upper() == "YES"
attrition_count = int(is_yes.sum())
total_headcount = len(filtered_df)
active_headcount = total_headcount - attrition_count  # FIX: "Active Workforce" now excludes leavers
attrition_rate = (attrition_count / total_headcount * 100) if total_headcount > 0 else 0
avg_income = filtered_df.loc[~is_yes, "MonthlyIncome"].mean()  # active employees' current pay

col1, col2, col3 = st.columns(3)
col1.metric("Active Workforce", f"{active_headcount:,}")
col2.metric("Attrition Rate %", f"{attrition_rate:.1f}%")
col3.metric("Average Monthly Income", f"${avg_income:,.2f}")

st.markdown("---")

# 5. Core Chart Interactivity
col_left, col2_right = st.columns(2)

with col_left:
    st.subheader("Turnover Breakdown by Job Role")
    fig_role = px.histogram(
        filtered_df,
        x="JobRole",
        color="Attrition",
        barmode="group",
        color_discrete_map={"No": "#0ea5e9", "Yes": "#ef4444"},
        labels={"JobRole": "Operational Role", "count": "Headcount"},
        template="plotly_dark",
    )
    fig_role.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_role, use_container_width=True)

with col2_right:
    st.subheader("Job Satisfaction vs. Employee Attrition")
    fig_sat = px.histogram(
        filtered_df,
        x="JobSatisfaction",
        color="Attrition",
        barmode="group",
        color_discrete_map={"No": "#10b981", "Yes": "#f97316"},
        labels={"JobSatisfaction": "Satisfaction Tier (1-4 Metric)", "count": "Responses"},
        template="plotly_dark",
    )
    fig_sat.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_sat, use_container_width=True)
