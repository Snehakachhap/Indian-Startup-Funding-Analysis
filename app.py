import streamlit as st
import pandas as pd

# Import analysis modules
from analysis.overall_analysis import show_overall_analysis
from analysis.industry_analysis import show_industry_analysis
from analysis.investor_analysis import show_investor_analysis
from analysis.startup_growth import show_startup_growth

# Import helper
from utils.helpers import clean_data


# Load and clean dataset
@st.cache_data
def load_data():
    df, report = clean_data("data/indian_startup_funding.csv")
    return df, report

df, cleaning_report = load_data()


# Sidebar for navigation
st.sidebar.title("Indian Startup Funding Analysis")
analysis_option = st.sidebar.radio(
    "Select Analysis Section:",
    (
        "Overall Funding Analysis", 
        "Industry-Wise Analysis", 
        "Investor Analysis", 
        "Startup Growth Analysis"
    )
)


# Show selected analysis
if analysis_option == "Overall Funding Analysis":
    show_overall_analysis(df, cleaning_report)

elif analysis_option == "Industry-Wise Analysis":
    show_industry_analysis(df)

elif analysis_option == "Investor Analysis":
    show_investor_analysis(df)

elif analysis_option == "Startup Growth Analysis":
    show_startup_growth(df)
