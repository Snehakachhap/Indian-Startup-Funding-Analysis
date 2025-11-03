import streamlit as st
import plotly.express as px

def show_overall_analysis(df, report=None):
    st.header("Overall Funding Analysis")
    
    # Cleaning Summary
    
    if report:
        st.subheader("🧹 Data Cleaning Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📂 Initial Rows", report["initial_rows"])
        with col2:
            st.metric("✅ Final Rows", report["final_rows"])
        with col3:
            st.metric("🗑️ Rows Dropped", report["rows_dropped"])

        col4, col5 = st.columns(2)
        with col4:
            st.metric("🌀 Duplicates Removed", report["duplicates_removed"])
        with col5:
            st.write("🔧 **Missing Values Handled:**")
            st.json(report["missing_values_handled"])
        
        st.markdown("---")  # separator

    
    # Total Funding
    
    total_funding = df['amount_in_usd'].sum()
    st.metric("💰 Total Funding (USD)", f"${total_funding:,.0f}")
    st.markdown("---")  # separator

   
    # Funding by Year
   
    funding_by_year = df.groupby("year")["amount_in_usd"].sum().reset_index()
    fig1 = px.line(
        funding_by_year, x="year", y="amount_in_usd",
        title="Funding Trend by Year", markers=True,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("---")  # separator

    
    # Top 10 Startups by Funding
    
    top_startups = df.groupby("startup_name")["amount_in_usd"].sum().nlargest(10).reset_index()
    fig2 = px.bar(
        top_startups, x="startup_name", y="amount_in_usd",
        title="Top 10 Funded Startups", color="amount_in_usd",
        color_continuous_scale="Teal"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")  # separator

   
    # Top 10 Industries
   
    top_industries = df.groupby("industry")["amount_in_usd"].sum().nlargest(10).reset_index()
    fig3 = px.pie(
        top_industries, names="industry", values="amount_in_usd",
        title="Top 10 Industries by Funding", hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("---")  # separator


    # Top Locations by Funding
    
    top_locations = df.groupby("location")["amount_in_usd"].sum().nlargest(10).reset_index()
    fig4 = px.bar(
        top_locations, x="location", y="amount_in_usd",
        title="Top Locations by Total Funding", color="location",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig4, use_container_width=True)
