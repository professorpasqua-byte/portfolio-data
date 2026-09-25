import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration & Theme setup
st.set_page_config(page_title="Tallywell Funnel Insights", layout="wide", initial_sidebar_state="expanded")

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
    df = pd.read_csv(
        "project-3-funnel-testing/tallywell_funnel_clean.csv",
        dtype={"CompletedSignup": "bool"},
    )
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: 'tallywell_funnel_clean.csv' not found inside project-3-funnel-testing folder!")
    st.stop()

# 3. Sidebar Filtering
st.sidebar.header("Session Filters")
device_filter = st.sidebar.selectbox("Filter by Device", ["All Devices"] + sorted(df["DeviceType"].dropna().unique()))

filtered_df = df if device_filter == "All Devices" else df[df["DeviceType"] == device_filter]

# 4. Core Conversion KPIs
st.subheader("Signup Funnel Performance Baseline")
total_sessions = len(filtered_df)
a_df = filtered_df[filtered_df["AssignedVariant"] == "Variant A"]
b_df = filtered_df[filtered_df["AssignedVariant"] == "Variant B"]

cr_a = (a_df["CompletedSignup"].sum() / len(a_df) * 100) if len(a_df) > 0 else 0
cr_b = (b_df["CompletedSignup"].sum() / len(b_df) * 100) if len(b_df) > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Funnel Traffic", f"{total_sessions:,} Sessions")
col2.metric("Variant A Conversion (12 fields)", f"{cr_a:.1f}%")
col3.metric("Variant B Conversion (4 fields)", f"{cr_b:.1f}%")

st.markdown("---")

# 5. Completion by variant, and where Variant A actually lost people
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Completion by Variant")
    completion = pd.DataFrame({
        "Variant": ["Variant A, 12 fields", "Variant B, 4 fields"],
        "Conversion": [cr_a, cr_b],
    })
    fig_completion = px.bar(
        completion, x="Variant", y="Conversion",
        color="Variant",
        color_discrete_map={"Variant A, 12 fields": "#ef4444", "Variant B, 4 fields": "#34d399"},
        labels={"Conversion": "Completion Rate %"},
        template="plotly_dark",
    )
    fig_completion.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig_completion, use_container_width=True)

with col_right:
    st.subheader("Where Variant A Lost People")
    dropoffs = a_df[~a_df["CompletedSignup"]]["DropoffField"].value_counts(normalize=True).reset_index()
    dropoffs.columns = ["Field", "Share"]
    dropoffs["Share"] = dropoffs["Share"] * 100
    dropoffs = dropoffs.sort_values("Share", ascending=True)

    fig_dropoff = px.bar(
        dropoffs, x="Share", y="Field", orientation="h",
        color="Share", color_continuous_scale="Reds",
        labels={"Share": "Share of Variant A Abandonment %", "Field": "Form Field"},
        template="plotly_dark",
    )
    fig_dropoff.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
    st.plotly_chart(fig_dropoff, use_container_width=True)
