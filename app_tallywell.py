import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration & Custom Theme setup
st.set_page_config(page_title="Tallywell Funnel Insights", layout="wide", initial_sidebar_state="expanded")

# Force clean dark styling accents
st.markdown("""
    <style>
    .main { background-color: #0d0e15; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #10b981; font-size: 2.2rem; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #9ca3af; font-size: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("Tallywell Product Funnel Optimization Analytics")
st.caption("Growth Engineering pipeline evaluating BJ Fogg's Behavior Model (Ability/Friction vs Motivation).")

# 2. Data Loading
@st.cache_data
def load_data():
    # 🔥 CRITICAL PATH FIXED: Explicitly routes straight to your engineered project directory
    df = pd.read_csv("project-3-funnel-testing/tallywell_funnel_clean.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: 'tallywell_funnel_clean.csv' path alignment mismatch! Check your folder layout structures.")
    st.stop()

# 3. Sidebar Filtering
st.sidebar.header("Product Demographics")
device_filter = st.sidebar.selectbox("Filter by Mobile OS", ["All Devices"] + list(df["DeviceType"].dropna().unique()))

filtered_df = df if device_filter == "All Devices" else df[df["DeviceType"] == device_filter]

# 4. Conversion Core Metrics Grid
st.subheader("Signup Funnel Performance Baseline")
total_users = len(filtered_df)
control_df = filtered_df[filtered_df["AssignedVariant"] == "Control"]
experiment_df = filtered_df[filtered_df["AssignedVariant"] == "Experiment"]

cr_control = (control_df["CompletedSignup"].sum() / len(control_df) * 100) if len(control_df) > 0 else 0
cr_experiment = (experiment_df["CompletedSignup"].sum() / len(experiment_df) * 100) if len(experiment_df) > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Funnel Traffic", f"{total_users:,} Sessions")
col2.metric("Control Conversion (Manual)", f"{cr_control:.1f}%")
col3.metric("Experiment Conversion (API)", f"{cr_experiment:.1f}%")

st.markdown("---")

# 5. Advanced Conversion Funnel Visualizations
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Funnel Conversion Shifts by Testing Group")
    funnel_stages = filtered_df.groupby(["AssignedVariant", "StepReached"]).size().reset_index(name="Users")
    
    fig_funnel = px.bar(
        funnel_stages,
        x="StepReached",
        y="Users",
        color="AssignedVariant",
        barmode="group",
        color_discrete_map={"Control": "#ef4444", "Experiment": "#34d399"},
        category_orders={"StepReached": ["Started", "IdentityVerified", "BankLinkingAttempted", "Completed"]},
        labels={"StepReached": "Funnel Milestone Reached", "Users": "Active Sessions"},
        template="plotly_dark"
    )
    fig_funnel.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_right:
    st.subheader("Session Duration Performance Metrics")
    fig_time = px.histogram(
        filtered_df,
        x="DurationMin",
        color="AssignedVariant",
        marginal="box",
        color_discrete_map={"Control": "#f43f5e", "Experiment": "#60a5fa"},
        labels={"DurationMin": "Total Funnel Time Elapsed (Minutes)"},
        template="plotly_dark"
    )
    fig_time.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", barmode="overlay")
    st.plotly_chart(fig_time, use_container_width=True)
