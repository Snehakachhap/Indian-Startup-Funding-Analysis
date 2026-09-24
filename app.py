import streamlit as st
import pandas as pd

from utils.data_loader import (
    load_data,
    get_filter_options,
    apply_filters
)

from utils.charts import (
    section_a_charts,
    section_b_charts,
    section_c_charts,
    section_d_charts,
    section_e_charts,
    section_f_charts
)

from utils.insights import (
    build_insights
)


# Page setup
st.set_page_config(
    page_title="Indian Startup Funding Analysis",
    page_icon="📊",
    layout="wide"
)


# Simple dashboard styling
st.markdown(
    """
    <style>

    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #666;
        font-size: 15px;
        margin-bottom: 20px;
    }

    .insight-card {
        background-color: #f8f9fa;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        min-height: 78px;
    }

    .insight-title {
        font-size: 13px;
        font-weight: 700;
        color: #555;
        margin-bottom: 5px;
    }

    .insight-text {
        font-size: 14px;
        color: #0B2E59;
        line-height: 1.4;
    }

    .kpi-card {
        background-color: #f8f9fa;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }

    .kpi-label {
        font-size: 13px;
        font-weight: 700; 
        color: #555;
    }

    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: #0B2E59;  
        margin-top: 4px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Load data
deals, investors = load_data()


# Get filter options
options = get_filter_options(deals)


# Sidebar
st.sidebar.title("Filters")


# Reset filters
if st.sidebar.button(
    "Reset Filters",
    use_container_width=True
):

    st.session_state.clear()
    st.rerun()


# Year filter
years = options["years"]

if years:

    selected_years = st.sidebar.slider(
        "Deal Year",
        min_value=min(years),
        max_value=max(years),
        value=(
            min(years),
            max(years)
        )
    )

else:

    selected_years = (0, 0)


# Industry filter
selected_industries = st.sidebar.multiselect(
    "Industry",
    options["industries"]
)


# City filter
selected_cities = st.sidebar.multiselect(
    "City",
    options["cities"]
)


# Investment type filter
selected_investment_types = st.sidebar.multiselect(
    "Investment Type",
    options["investment_types"]
)


# Disclosed amount filter
disclosed_only = st.sidebar.checkbox(
    "Only disclosed amounts"
)


# Startup search
startup_search = st.sidebar.text_input(
    "Search startup"
)


# Apply filters
filtered_deals = apply_filters(
    deals,
    selected_years,
    selected_industries,
    selected_cities,
    selected_investment_types,
    disclosed_only,
    startup_search
)


# Page heading
st.markdown(
    '<div class="main-title">Indian Startup Funding Analysis 📊</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Funding trends, industries, cities, startups, investment types and investors</div>',
    unsafe_allow_html=True
)


# KPI calculations
total_funding = filtered_deals[
    "amount_usd"
].sum()

funding_deals = filtered_deals[
    "amount_disclosed"
].sum()

average_deal = (
    filtered_deals[
        filtered_deals["amount_disclosed"]
    ]["amount_usd"].mean()
)

startup_count = filtered_deals[
    "startup"
].nunique()

disclosure_rate = (
    filtered_deals["amount_disclosed"].mean()
    * 100
    if len(filtered_deals) > 0
    else 0
)


def format_money(value):

    if pd.isna(value):
        return "$0"

    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"

    return f"${value:,.0f}"


# KPI section
st.subheader("Key Metrics")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)


with kpi1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Funding</div>
            <div class="kpi-value">{format_money(total_funding)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Funding Deals</div>
            <div class="kpi-value">{int(funding_deals):,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Deal</div>
            <div class="kpi-value">{format_money(average_deal)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Startups</div>
            <div class="kpi-value">{startup_count:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi5:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Disclosure Rate</div>
            <div class="kpi-value">{disclosure_rate:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("")


# Business insights
st.subheader("Key Business Insights")

insights = build_insights(
    filtered_deals,
    investors
)

insight_columns = st.columns(
    len(insights)
)

for column, insight in zip(
    insight_columns,
    insights
):

    with column:

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">
                    {insight["title"]}
                </div>
                <div class="insight-text">
                    {insight["text"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

startup_options = sorted(
    filtered_deals["startup"]
    .dropna()
    .unique()
    .tolist()
)

startup_focus = st.sidebar.selectbox(
    "Select a startup",
    ["None"] + startup_options
)

if startup_focus == "None":
    startup_focus = None


# Analysis tabs
tabs = st.tabs(
    [
        "Overview & Trends",
        "Industry-wise Analysis",
        "City-wise Analysis",
        "Startups-wise Analysis",
        "Investment Type Analysis",
        "Investors-wise Analysis"
    ]
)


# Helper to display charts
def display_charts(
    charts,
    columns=2
):

    for index in range(
        0,
        len(charts),
        columns
    ):

        row = charts[
            index:index + columns
        ]

        chart_columns = st.columns(
            len(row)
        )

        for column, chart in zip(
            chart_columns,
            row
        ):

            with column:

                st.plotly_chart(
                    chart,
                    use_container_width=True
                )


# Overview
with tabs[0]:

    st.caption(
        "Funding growth, deal activity and disclosure trends over time."
    )

    charts = section_a_charts(
        filtered_deals
    )

    display_charts(charts)


# Industry
with tabs[1]:

    st.caption(
        "Compare funding, deal activity and average deal size across industries."
    )

    charts = section_b_charts(
        filtered_deals
    )

    display_charts(charts)


# City
with tabs[2]:

    st.caption(
        "Explore startup funding activity across major Indian cities."
    )

    charts = section_c_charts(
        filtered_deals
    )

    display_charts(charts)


# Startups
with tabs[3]:

    st.caption(
        "Compare startups by funding, funding rounds and major deals."
    )

    charts = section_d_charts(
        filtered_deals,
        startup_focus
    )

    display_charts(charts)


# Investment type
with tabs[4]:

    st.caption(
        "Analyze funding patterns across different investment types."
    )

    charts = section_e_charts(
        filtered_deals
    )

    display_charts(charts)


# Investors
with tabs[5]:

    st.caption(
        "Analyze investor participation, co-investment and startup coverage."
    )

    charts = section_f_charts(
        filtered_deals,
        investors
    )

    display_charts(charts)
