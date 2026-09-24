import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration & Custom Theme
st.set_page_config(page_title="Solmere Behavioral Churn Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #f43f5e; font-size: 2.2rem; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #9ca3af; font-size: 1rem; }
    </style>
""", unsafe_allow_index=True)

st.title("Solmere Platform Churn Diagnostics Dashboard")
st.caption("Behavioral Economics analytics pipeline investigating the Peak-End Rule and customer churn indicators.")

# 2. Data Loading
@st.cache_data
def load_data():
    # Adjusted cleanly to target your project folder path
    df = pd.read_csv("project-2-behavioral-churn/solmere_churn_clean.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: 'solmere_churn_clean.csv' not found inside project-2-behavioral-churn folder!")
    st.stop()

# 3. Sidebar Filtering
st.sidebar.header("Regional Filters")
region_filter = st.sidebar.selectbox("Select Geographical Region", ["All Regions"] + list(df["Region"].dropna().unique()))
plan_filter = st.sidebar.selectbox("Select Subscription Tier", ["All Plans"] + list(df["Plan"].dropna().unique()))

# Chain filtering logic interactively
filtered_df = df
if region_filter != "All Regions":
    filtered_df = filtered_df[filtered_df["Region"] == region_filter]
if plan_filter != "All Plans":
    filtered_df = filtered_df[filtered_df["Plan"] == plan_filter]

# 4. Core Dynamic Analytics KPIs
st.subheader("Diagnostic Subscription Performance")
total_subs = len(filtered_df)

# Direct boolean handling calculation safely
churn_count = filtered_df["Cancelled"].sum()
churn_rate = (churn_count / total_subs * 100) if total_subs > 0 else 0
total_mrr = filtered_df["TotalSpent"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Monitored Cohort", f"{total_subs:,} Users")
col2.metric("Observed Churn Rate %", f"{churn_rate:.1f}%")
col3.metric("Accumulated Value (LTV)", f"${total_mrr:,.2f}")

st.markdown("---")

# 5. Dynamic Visualizations proving the core hypothesis
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Churn Rates vs. Pre-Renewal Negative Tickets")
    churn_analysis = filtered_df.groupby("HasNegativeTicketPreRenewal")["Cancelled"].mean().reset_index()
    churn_analysis["Cancelled"] = churn_analysis["Cancelled"] * 100
    churn_analysis["HasNegativeTicketPreRenewal"] = churn_analysis["HasNegativeTicketPreRenewal"].map({True: "Had Bad Support Experience", False: "Clean Support Window"})
    
    fig_hypothesis = px.bar(
        churn_analysis,
        x="HasNegativeTicketPreRenewal",
        y="Cancelled",
        color="HasNegativeTicketPreRenewal",
        color_discrete_map={"Had Bad Support Experience": "#e11d48", "Clean Support Window": "#10b981"},
        labels={"Cancelled": "Calculated Cancellation Rate %", "HasNegativeTicketPreRenewal": "User Support History"},
        template="plotly_dark"
    )
    fig_hypothesis.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig_hypothesis, use_container_width=True)

with col_right:
    st.subheader("Distribution of User Experience Scores")
    fig_score = px.box(
        filtered_df,
        x="Plan",
        y="OnboardingScore",
        color="Cancelled",
        color_discrete_map={True: "#ef4444", False: "#38bdf8"},
        labels={"OnboardingScore": "Onboarding UX Grade (0-100)", "Plan": "Subscription Tier"},
        template="plotly_dark"
    )
    fig_score.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_score, use_container_width=True)
