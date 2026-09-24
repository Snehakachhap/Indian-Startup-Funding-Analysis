import pandas as pd
import plotly.express as px

def _empty_fig(message="No data for the current filter selection"):

    fig = px.scatter()

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text=message,
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=15)
            )
        ],
        height=320
    )

    return fig


def _style(fig, height=400):

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=55, b=40),
        template="plotly_white",
        legend_title_text=""
    )

    return fig


# Section A: Overview and Trends

def section_a_charts(df):

    if df.empty:
        return [_empty_fig()]

    yearly = (
        df.groupby("deal_year")
        .agg(
            total_deals=("deal_id", "count"),
            total_funding=("amount_usd", "sum")
        )
        .reset_index()
    )

    # Total funding by year
    fig1 = px.bar(
        yearly,
        x="deal_year",
        y="total_funding",
        title="Total Funding by Year",
        labels={
            "deal_year": "Year",
            "total_funding": "Funding (USD)"
        }
    )

    # Number of deals by year
    fig2 = px.line(
        yearly,
        x="deal_year",
        y="total_deals",
        title="Number of Deals by Year",
        markers=True,
        labels={
            "deal_year": "Year",
            "total_deals": "Deals"
        }
    )

    # Year-over-year funding growth
    yearly["previous_funding"] = yearly["total_funding"].shift(1)

    yearly["growth_pct"] = (
        (
            yearly["total_funding"]
            - yearly["previous_funding"]
        )
        / yearly["previous_funding"]
        * 100
    )

    growth = yearly.dropna(
        subset=["growth_pct"]
    )

    fig3 = px.bar(
        growth,
        x="deal_year",
        y="growth_pct",
        title="YoY Funding Growth (%)",
        labels={
            "deal_year": "Year",
            "growth_pct": "Growth (%)"
        }
    )

    # Average disclosed deal size
    average_deal = (
        df[df["amount_disclosed"]]
        .groupby("deal_year")["amount_usd"]
        .mean()
        .reset_index()
    )

    fig4 = px.line(
        average_deal,
        x="deal_year",
        y="amount_usd",
        title="Average Deal Size by Year",
        markers=True,
        labels={
            "deal_year": "Year",
            "amount_usd": "Average Deal Size (USD)"
        }
    )

    # Disclosure status
    disclosure = (
        df.groupby(
            ["deal_year", "amount_disclosed"]
        )
        .size()
        .reset_index(name="deal_count")
    )

    disclosure["status"] = disclosure[
        "amount_disclosed"
    ].map(
        {
            True: "Disclosed",
            False: "Undisclosed"
        }
    )

    fig5 = px.bar(
        disclosure,
        x="deal_year",
        y="deal_count",
        color="status",
        title="Disclosed vs Undisclosed Deals",
        barmode="stack",
        labels={
            "deal_year": "Year",
            "deal_count": "Deals",
            "status": "Amount Status"
        }
    )

    return [
        _style(fig1),
        _style(fig2),
        _style(fig3),
        _style(fig4),
        _style(fig5)
    ]


# Section B: Industry Analysis

def section_b_charts(df):

    df = df[df["industry"] != "Unknown"]

    if df.empty:
        return [_empty_fig()]

    # Funding by industry
    industry_funding = (
        df.groupby("industry")["amount_usd"]
        .sum()
        .nlargest(10)
        .reset_index()
    )

    fig1 = px.bar(
        industry_funding,
        x="industry",
        y="amount_usd",
        title="Top 10 Industries by Total Funding",
        labels={
            "industry": "Industry",
            "amount_usd": "Funding (USD)"
        }
    )

    # Number of deals
    industry_deals = (
        df.groupby("industry")
        .size()
        .nlargest(10)
        .reset_index(name="deal_count")
    )

    fig2 = px.bar(
        industry_deals,
        x="industry",
        y="deal_count",
        title="Top 10 Industries by Number of Deals",
        labels={
            "industry": "Industry",
            "deal_count": "Deals"
        }
    )

    # Average deal size
    industry_average = (
        df[df["amount_disclosed"]]
        .groupby("industry")
        .agg(
            disclosed_deals=("amount_usd", "count"),
            average_deal=("amount_usd", "mean")
        )
        .reset_index()
    )

    industry_average = (
        industry_average[
            industry_average["disclosed_deals"] >= 5
        ]
        .sort_values(
            "average_deal",
            ascending=False
        )
        .head(15)
    )

    fig3 = px.bar(
        industry_average,
        x="industry",
        y="average_deal",
        title="Average Deal Size by Industry",
        labels={
            "industry": "Industry",
            "average_deal": "Average Deal Size (USD)"
        }
    )

    # Early vs recent period
    comparison = df.copy()

    comparison["period"] = comparison[
        "deal_year"
    ].apply(
        lambda year:
        "2015-2018"
        if 2015 <= year <= 2018
        else (
            "2021-2024"
            if 2021 <= year <= 2024
            else None
        )
    )

    comparison = comparison.dropna(
        subset=["period"]
    )

    if comparison.empty:

        fig4 = _empty_fig(
            "No deals in the selected comparison periods"
        )

    else:

        period_data = (
            comparison
            .groupby(
                ["industry", "period"]
            )["amount_usd"]
            .sum()
            .reset_index()
        )

        fig4 = px.bar(
            period_data,
            x="industry",
            y="amount_usd",
            color="period",
            barmode="group",
            title="Industry Funding: 2015-2018 vs 2021-2024",
            labels={
                "industry": "Industry",
                "amount_usd": "Funding (USD)",
                "period": "Period"
            }
        )

    # Industry funding heatmap
    top_industries = (
        df.groupby("industry")["amount_usd"]
        .sum()
        .nlargest(5)
        .index
    )

    heatmap = (
        df[df["industry"].isin(top_industries)]
        .groupby(
            ["industry", "deal_year"]
        )["amount_usd"]
        .sum()
        .reset_index()
    )

    if heatmap.empty:

        fig5 = _empty_fig()

    else:

        heatmap = heatmap.pivot(
            index="industry",
            columns="deal_year",
            values="amount_usd"
        ).fillna(0)

        fig5 = px.imshow(
            heatmap,
            title="Funding Heatmap: Top 5 Industries",
            labels={
                "x": "Year",
                "y": "Industry",
                "color": "Funding (USD)"
            },
            aspect="auto"
        )

    return [
        _style(fig1),
        _style(fig2),
        _style(fig3),
        _style(fig4),
        _style(fig5)
    ]


# Section C: City and Geography Analysis

def section_c_charts(df):

    df = df[df["city"] != "Unknown"]

    if df.empty:
        return [_empty_fig()]

    # Funding by city
    city_funding = (
        df.groupby("city")["amount_usd"]
        .sum()
        .nlargest(10)
        .reset_index()
    )

    fig1 = px.bar(
        city_funding,
        x="city",
        y="amount_usd",
        title="Top 10 Cities by Total Funding",
        labels={
            "city": "City",
            "amount_usd": "Funding (USD)"
        }
    )

    # Number of deals
    city_deals = (
        df.groupby("city")
        .size()
        .nlargest(10)
        .reset_index(name="deal_count")
    )

    fig2 = px.bar(
        city_deals,
        x="city",
        y="deal_count",
        title="Top 10 Cities by Number of Deals",
        labels={
            "city": "City",
            "deal_count": "Deals"
        }
    )

    # Average deal size
    city_average = (
        df[df["amount_disclosed"]]
        .groupby("city")
        .agg(
            disclosed_deals=("amount_usd", "count"),
            average_deal=("amount_usd", "mean")
        )
        .reset_index()
    )

    city_average = (
        city_average[
            city_average["disclosed_deals"] >= 5
        ]
        .sort_values(
            "average_deal",
            ascending=False
        )
        .head(15)
    )

    fig3 = px.bar(
        city_average,
        x="city",
        y="average_deal",
        title="Average Deal Size by City",
        labels={
            "city": "City",
            "average_deal": "Average Deal Size (USD)"
        }
    )

    # Seed/Angel vs Private Equity
    top_cities = (
        df.groupby("city")
        .size()
        .nlargest(10)
        .index
    )

    stage_data = df[
        df["city"].isin(top_cities)
        & df["investment_type"].isin(
            ["Seed/Angel", "Private Equity"]
        )
    ]

    if stage_data.empty:

        fig4 = _empty_fig(
            "No Seed/Angel or Private Equity deals"
        )

    else:

        stage_data = (
            stage_data
            .groupby(
                ["city", "investment_type"]
            )
            .size()
            .reset_index(name="deal_count")
        )

        fig4 = px.bar(
            stage_data,
            x="city",
            y="deal_count",
            color="investment_type",
            barmode="stack",
            title="Seed/Angel vs Private Equity Deals",
            labels={
                "city": "City",
                "deal_count": "Deals",
                "investment_type": "Investment Type"
            }
        )

    return [
        _style(fig1),
        _style(fig2),
        _style(fig3),
        _style(fig4)
    ]


# Section D: Startups Analysis

def section_d_charts(
    df,
    startup_focus=None
):

    if df.empty:
        return [_empty_fig()]

    # Total funding by startup
    startup_funding = (
        df[df["amount_disclosed"]]
        .groupby("startup")
        .agg(
            total_rounds=("deal_id", "count"),
            total_funding=("amount_usd", "sum")
        )
        .reset_index()
        .sort_values(
            "total_funding",
            ascending=False
        )
        .head(10)
    )

    fig1 = px.bar(
        startup_funding,
        x="startup",
        y="total_funding",
        title="Top 10 Startups by Total Funding Raised",
        hover_data=["total_rounds"],
        labels={
            "startup": "Startup",
            "total_funding": "Funding (USD)"
        }
    )

    # Funding rounds by startup
    startup_rounds = (
        df.groupby("startup")
        .size()
        .nlargest(10)
        .reset_index(name="total_rounds")
    )

    fig2 = px.bar(
        startup_rounds,
        x="startup",
        y="total_rounds",
        title="Top 10 Startups by Number of Funding Rounds",
        labels={
            "startup": "Startup",
            "total_rounds": "Funding Rounds"
        }
    )

    # Largest individual deals
    largest_deals = (
        df[df["amount_disclosed"]]
        .sort_values(
            "amount_usd",
            ascending=False
        )
        .head(10)
    )

    fig3 = px.bar(
        largest_deals,
        x="startup",
        y="amount_usd",
        color="investment_type",
        title="Top 10 Largest Single Deals",
        hover_data=[
            "deal_date",
            "city",
            "industry"
        ],
        labels={
            "startup": "Startup",
            "amount_usd": "Deal Amount (USD)",
            "investment_type": "Investment Type"
        }
    )

    # Funding timeline of top startups
    top_startups = (
        df[df["amount_disclosed"]]
        .groupby("startup")["amount_usd"]
        .sum()
        .nlargest(5)
        .index
    )

    timeline = df[
        df["startup"].isin(top_startups)
        & df["amount_disclosed"]
    ].sort_values("deal_date")

    fig4 = px.line(
        timeline,
        x="deal_date",
        y="amount_usd",
        color="startup",
        markers=True,
        title="Funding Timeline: Top 5 Startups",
        hover_data=[
            "investment_type",
            "city"
        ],
        labels={
            "deal_date": "Date",
            "amount_usd": "Deal Amount (USD)",
            "startup": "Startup"
        }
    )

    charts = [
        fig1,
        fig2,
        fig3,
        fig4
    ]

    # Selected startup deep dive
    if startup_focus:

        startup_data = df[
            df["startup"] == startup_focus
        ].sort_values("deal_date")

        if not startup_data.empty:

            fig5 = px.bar(
                startup_data,
                x="deal_date",
                y="amount_usd",
                color="investment_type",
                title=f"Funding Timeline: {startup_focus}",
                hover_data=[
                    "city",
                    "industry",
                    "investors"
                ],
                labels={
                    "deal_date": "Date",
                    "amount_usd": "Deal Amount (USD)",
                    "investment_type": "Investment Type"
                }
            )

            charts.append(fig5)

    return [
        _style(fig)
        for fig in charts
    ]


# Section E: Investment Type Analysis

def section_e_charts(df):

    if df.empty:
        return [_empty_fig()]

    # Funding by investment type
    type_summary = (
        df.groupby("investment_type")
        .agg(
            total_deals=("deal_id", "count"),
            total_funding=("amount_usd", "sum")
        )
        .reset_index()
        .sort_values(
            "total_funding",
            ascending=False
        )
    )

    fig1 = px.bar(
        type_summary,
        x="investment_type",
        y="total_funding",
        title="Total Funding by Investment Type",
        hover_data=["total_deals"],
        labels={
            "investment_type": "Investment Type",
            "total_funding": "Funding (USD)"
        }
    )

    # Average deal size
    type_average = (
        df[df["amount_disclosed"]]
        .groupby("investment_type")
        .agg(
            disclosed_deals=("amount_usd", "count"),
            average_deal=("amount_usd", "mean")
        )
        .reset_index()
    )

    type_average = (
        type_average[
            type_average["disclosed_deals"] >= 5
        ]
        .sort_values(
            "average_deal",
            ascending=False
        )
    )

    fig2 = px.bar(
        type_average,
        x="investment_type",
        y="average_deal",
        title="Average Deal Size by Investment Type",
        labels={
            "investment_type": "Investment Type",
            "average_deal": "Average Deal Size (USD)"
        }
    )

    # Number of deals by investment type and year
    type_year = (
        df.groupby(
            ["deal_year", "investment_type"]
        )
        .size()
        .reset_index(name="deal_count")
    )

    fig3 = px.bar(
        type_year,
        x="deal_year",
        y="deal_count",
        color="investment_type",
        barmode="stack",
        title="Investment Type Mix by Year",
        labels={
            "deal_year": "Year",
            "deal_count": "Deals",
            "investment_type": "Investment Type"
        }
    )

    # Percentage share
    type_year["percentage"] = (
        type_year
        .groupby("deal_year")["deal_count"]
        .transform(
            lambda x: x / x.sum() * 100
        )
    )

    fig4 = px.bar(
        type_year,
        x="deal_year",
        y="percentage",
        color="investment_type",
        barmode="stack",
        title="Investment Type Mix by Year (%)",
        labels={
            "deal_year": "Year",
            "percentage": "Share (%)",
            "investment_type": "Investment Type"
        }
    )

    return [
        _style(fig1),
        _style(fig2),
        _style(fig3),
        _style(fig4)
    ]


# Section F: Investors Analysis

def section_f_charts(
    df,
    investors_df
):

    if df.empty:
        return [_empty_fig()]

    deal_ids = set(
        df["deal_id"]
    )

    investor_data = investors_df[
        investors_df["deal_id"].isin(deal_ids)
    ]

    if investor_data.empty:
        return [
            _empty_fig(
                "No investor data for the current filters"
            )
        ]

    # Top investors by number of deals
    top_investors = (
        investor_data
        .groupby("investor")["deal_id"]
        .nunique()
        .nlargest(15)
        .reset_index(
            name="deals_participated"
        )
    )

    fig1 = px.bar(
        top_investors,
        x="investor",
        y="deals_participated",
        title="Top 15 Investors by Number of Deals",
        labels={
            "investor": "Investor",
            "deals_participated": "Deals"
        }
    )

    # Total amount involved
    disclosed_deals = df[
        df["amount_disclosed"]
    ][
        ["deal_id", "amount_usd"]
    ]

    investor_amounts = investor_data.merge(
        disclosed_deals,
        on="deal_id"
    )

    investor_amounts = (
        investor_amounts
        .groupby("investor")
        .agg(
            deals_participated=(
                "deal_id",
                "nunique"
            ),
            total_amount=(
                "amount_usd",
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "total_amount",
            ascending=False
        )
        .head(15)
    )

    fig2 = px.bar(
        investor_amounts,
        x="investor",
        y="total_amount",
        title="Top 15 Investors by Total Amount Involved",
        hover_data=[
            "deals_participated"
        ],
        labels={
            "investor": "Investor",
            "total_amount": "Amount Involved (USD)"
        }
    )

    # Co-investor pairs
    pairs = investor_data.merge(
        investor_data,
        on="deal_id"
    )

    pairs = pairs[
        pairs["investor_x"]
        < pairs["investor_y"]
    ]

    if pairs.empty:

        fig3 = _empty_fig(
            "No co-investment pairs available"
        )

    else:

        pairs = (
            pairs
            .groupby(
                [
                    "investor_x",
                    "investor_y"
                ]
            )
            .size()
            .reset_index(
                name="co_investments"
            )
            .sort_values(
                "co_investments",
                ascending=False
            )
            .head(15)
        )

        pairs["investor_pair"] = (
            pairs["investor_x"]
            + " & "
            + pairs["investor_y"]
        )

        fig3 = px.bar(
            pairs,
            x="investor_pair",
            y="co_investments",
            title="Top 15 Co-Investor Pairs",
            labels={
                "investor_pair": "Investor Pair",
                "co_investments": "Co-Investments"
            }
        )

        fig3.update_layout(
            xaxis_tickangle=-45
        )

    # Average investors per deal
    average_investors = (
        df.groupby("deal_year")[
            "investor_count"
        ]
        .mean()
        .reset_index()
    )

    fig4 = px.line(
        average_investors,
        x="deal_year",
        y="investor_count",
        markers=True,
        title="Average Investors per Deal",
        labels={
            "deal_year": "Year",
            "investor_count": "Average Investors"
        }
    )

    # Unique startups backed
    investor_startups = investor_data.merge(
        df[
            ["deal_id", "startup"]
        ],
        on="deal_id"
    )

    unique_startups = (
        investor_startups
        .groupby("investor")
        .agg(
            unique_startups=(
                "startup",
                "nunique"
            ),
            total_deals=(
                "deal_id",
                "nunique"
            )
        )
        .reset_index()
        .sort_values(
            "unique_startups",
            ascending=False
        )
        .head(15)
    )

    fig5 = px.bar(
        unique_startups,
        x="investor",
        y="unique_startups",
        title="Top 15 Investors by Unique Startups Backed",
        hover_data=[
            "total_deals"
        ],
        labels={
            "investor": "Investor",
            "unique_startups": "Unique Startups"
        }
    )

    # Solo vs multiple investors
    investor_type = (
        df[df["amount_disclosed"]]
        .groupby("deal_type")
        .agg(
            total_deals=(
                "deal_id",
                "count"
            ),
            average_amount=(
                "amount_usd",
                "mean"
            )
        )
        .reset_index()
    )

    fig6 = px.bar(
        investor_type,
        x="deal_type",
        y="average_amount",
        title="Average Deal Size: Solo vs Multiple Investors",
        hover_data=[
            "total_deals"
        ],
        labels={
            "deal_type": "Deal Type",
            "average_amount": "Average Deal Size (USD)"
        }
    )

    return [
        _style(fig1),
        _style(fig2),
        _style(fig3),
        _style(fig4),
        _style(fig5),
        _style(fig6)
    ]