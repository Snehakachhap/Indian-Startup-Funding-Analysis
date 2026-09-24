import pandas as pd

def format_usd(value):

    if pd.isna(value):
        return "$0"

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"

    return f"${value:,.0f}"


def build_insights(df, investors_df=None):

    if df.empty:
        return [
            {
                "title": "No Data",
                "text": "No deals match the current filters."
            }
        ]

    insights = []

    # Overall funding
    total_funding = df["amount_usd"].sum()
    total_deals = len(df)

    insights.append(
        {
            "title": "Funding Overview",
            "text": (
                f"{format_usd(total_funding)} across "
                f"{total_deals:,} deals."
            )
        }
    )

    # Funding peak year
    yearly = (
        df.groupby("deal_year")["amount_usd"]
        .sum()
    )

    if not yearly.empty:

        peak_year = yearly.idxmax()
        peak_funding = yearly.max()

        insights.append(
            {
                "title": "Peak Funding Year",
                "text": (
                    f"{int(peak_year)} recorded "
                    f"{format_usd(peak_funding)}."
                )
            }
        )

    # Leading industry
    industry_data = df[
        df["industry"] != "Unknown"
    ]

    if not industry_data.empty:

        industry = (
            industry_data
            .groupby("industry")["amount_usd"]
            .sum()
            .idxmax()
        )

        industry_funding = (
            industry_data
            .groupby("industry")["amount_usd"]
            .sum()
            .max()
        )

        insights.append(
            {
                "title": "Leading Industry",
                "text": (
                    f"{industry} received "
                    f"{format_usd(industry_funding)}."
                )
            }
        )

    # Leading city
    city_data = df[
        df["city"] != "Unknown"
    ]

    if not city_data.empty:

        city = (
            city_data
            .groupby("city")["amount_usd"]
            .sum()
            .idxmax()
        )

        city_funding = (
            city_data
            .groupby("city")["amount_usd"]
            .sum()
            .max()
        )

        insights.append(
            {
                "title": "Leading Startup Hub",
                "text": (
                    f"{city} recorded "
                    f"{format_usd(city_funding)}."
                )
            }
        )

    # Investor activity
    if investors_df is not None and not investors_df.empty:

        filtered_ids = set(
            df["deal_id"]
        )

        investor_data = investors_df[
            investors_df["deal_id"].isin(
                filtered_ids
            )
        ]

        if not investor_data.empty:

            investor = (
                investor_data
                .groupby("investor")["deal_id"]
                .nunique()
                .idxmax()
            )

            investor_deals = (
                investor_data
                .groupby("investor")["deal_id"]
                .nunique()
                .max()
            )

            insights.append(
                {
                    "title": "Active Investor",
                    "text": (
                        f"{investor} participated in "
                        f"{int(investor_deals):,} deals."
                    )
                }
            )

    return insights[:5]
