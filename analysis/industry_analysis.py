import streamlit as st
import plotly.express as px

def show_industry_analysis(df):
    st.header("Industry-Wise Analysis")

    # Industry Funding Distribution
    industry_funding = df.groupby("industry")["amount_in_usd"].sum().reset_index()
    fig1 = px.treemap(
        industry_funding,
        path=["industry"],
        values="amount_in_usd",
        title="Industry Funding Distribution",
        color="amount_in_usd",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("---")  # separator

    # Average Deal Size per Industry
    
    avg_funding = df.groupby("industry")["amount_in_usd"].mean().reset_index()
    top_avg_funding = avg_funding.sort_values("amount_in_usd", ascending=False).head(10)
    fig2 = px.bar(
        top_avg_funding,
        x="industry",
        y="amount_in_usd",
        title="Top 10 Industries by Average Deal Size",
        color="amount_in_usd",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")  # separator

    # Funding by Industry and Investment Type
    industry_investment = df.groupby(["industry", "investment_type"])["amount_in_usd"].sum().reset_index()
    fig3 = px.bar(
        industry_investment,
        x="industry",
        y="amount_in_usd",
        color="investment_type",
        barmode="stack",
        title="Funding by Industry and Investment Type"
    )
    st.plotly_chart(fig3, use_container_width=True)
