import streamlit as st
import plotly.express as px

def show_startup_growth(df):
    st.header("Startup Growth Analysis")

    
    # Top Startups by Number of Funding Rounds
    
    rounds = df.groupby("startup_name").size().nlargest(10).reset_index(name="rounds")
    fig1 = px.bar(
        rounds,
        x="startup_name",
        y="rounds",
        title="Top Startups by Funding Rounds",
        color="rounds",
        color_continuous_scale="Plasma"
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("---")  # separator

    
    # Funding Evolution of Top Startups
    
    top_startups = df.groupby("startup_name")["amount_in_usd"].sum().nlargest(5).index
    df_top = df[df["startup_name"].isin(top_startups)]
    fig2 = px.line(
        df_top,
        x="year",
        y="amount_in_usd",
        color="startup_name",
        title="Funding Evolution of Top Startups",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    st.plotly_chart(fig2, use_container_width=True)
