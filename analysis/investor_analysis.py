import streamlit as st
import plotly.express as px

def show_investor_analysis(df):
    st.header(" Investor Analysis")

    # Prepare Investors Data
    # Split multiple investors into separate rows
    investors_df = df.assign(investors=df["investors"].str.split(",")).explode("investors")
    investors_df["investors"] = investors_df["investors"].str.strip()
    st.markdown("---")  # separator

    # Top 10 Investors by Total Investment
    top_investors = investors_df.groupby("investors")["amount_in_usd"].sum().nlargest(10).reset_index()
    fig1 = px.bar(
        top_investors,
        x="investors",
        y="amount_in_usd",
        title="Top 10 Investors by Total Investment",
        color="amount_in_usd",
        color_continuous_scale="Sunset"
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("---")  # separator

    # Top 10 Investors by Number of Deals
    deals = investors_df.groupby("investors").size().nlargest(10).reset_index(name="deal_count")
    fig2 = px.bar(
        deals,
        x="investors",
        y="deal_count",
        title="Top 10 Investors by Number of Deals",
        color="deal_count",
        color_continuous_scale="Aggrnyl"
    )
    st.plotly_chart(fig2, use_container_width=True)
