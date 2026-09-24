import os
import numpy as np
import pandas as pd
import streamlit as st


# Data file paths
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)

DEALS_FILE = os.path.join(
    DATA_DIR,
    "Indian_startup_data_cleaned.csv"
)

INVESTORS_FILE = os.path.join(
    DATA_DIR,
    "deal_investors.csv"
)


# Handle small differences in column names
COLUMN_ALIASES = {
    "date": "deal_date",
    "year": "deal_year"
}


def standardize_columns(df):
    """Rename columns to the names used by the dashboard."""
    return df.rename(
        columns={
            old: new
            for old, new in COLUMN_ALIASES.items()
            if old in df.columns
        }
    )


@st.cache_data(show_spinner="Loading startup funding data...")
def load_data():

    # Check that both files exist
    if not os.path.exists(DEALS_FILE):
        return None, None

    if not os.path.exists(INVESTORS_FILE):
        return None, None

    # Load data
    deals = pd.read_csv(DEALS_FILE)
    investors = pd.read_csv(INVESTORS_FILE)

    # Standardize column names
    deals = standardize_columns(deals)
    investors = standardize_columns(investors)

    # Convert date
    deals["deal_date"] = pd.to_datetime(
        deals["deal_date"],
        errors="coerce",
        dayfirst=True
    )

    # Create year if it is not already available
    if "deal_year" not in deals.columns:
        deals["deal_year"] = deals["deal_date"].dt.year

    deals["deal_year"] = pd.to_numeric(
        deals["deal_year"],
        errors="coerce"
    ).astype("Int64")

    # Convert funding amount to numeric
    deals["amount_usd"] = pd.to_numeric(
        deals["amount_usd"],
        errors="coerce"
    )

    # Make sure amount_disclosed exists
    if "amount_disclosed" not in deals.columns:
        deals["amount_disclosed"] = deals["amount_usd"].notna()
    else:
        if deals["amount_disclosed"].dtype == object:
            deals["amount_disclosed"] = (
                deals["amount_disclosed"]
                .astype(str)
                .str.upper()
                .isin(["TRUE", "1", "YES"])
            )
        else:
            deals["amount_disclosed"] = deals["amount_disclosed"].fillna(False).astype(bool)

        deals["amount_disclosed"] = (
            deals["amount_disclosed"]
            & deals["amount_usd"].notna()
        )

    # Clean common text columns
    text_columns = [
        "startup",
        "industry",
        "sub_vertical",
        "city",
        "investment_type"
    ]

    for column in text_columns:
        if column in deals.columns:
            deals[column] = (
                deals[column]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
            )

            deals.loc[
                deals[column] == "",
                column
            ] = "Unknown"

    # Calculate investor count if not already available
    if "investor_count" not in deals.columns:

        deals["investor_count"] = (
            deals["investors"]
            .fillna("")
            .astype(str)
            .apply(
                lambda x: len(
                    [
                        investor
                        for investor in x.split(",")
                        if investor.strip()
                    ]
                )
            )
        )

    # Classify deals based on investor count
    deals["deal_type"] = np.where(
        deals["investor_count"] == 1,
        "Solo Investor",
        "Multiple Investors"
    )

    # Clean investor table
    if "investor" in investors.columns:
        investors["investor"] = (
            investors["investor"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    return deals, investors


def get_filter_options(deals):

    return {
        "years": sorted(
            deals["deal_year"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        ),

        "industries": sorted(
            [
                value
                for value in deals["industry"].unique()
                if value != "Unknown"
            ]
        ),

        "cities": sorted(
            [
                value
                for value in deals["city"].unique()
                if value != "Unknown"
            ]
        ),

        "investment_types": sorted(
            deals["investment_type"]
            .dropna()
            .unique()
            .tolist()
        )
    }


def apply_filters(
    deals,
    year_range,
    industries,
    cities,
    investment_types,
    disclosed_only,
    startup_query
):

    filtered = deals.copy()

    # Year filter
    filtered = filtered[
        (filtered["deal_year"] >= year_range[0])
        & (filtered["deal_year"] <= year_range[1])
    ]

    # Industry filter
    if industries:
        filtered = filtered[
            filtered["industry"].isin(industries)
        ]

    # City filter
    if cities:
        filtered = filtered[
            filtered["city"].isin(cities)
        ]

    # Investment type filter
    if investment_types:
        filtered = filtered[
            filtered["investment_type"].isin(investment_types)
        ]

    # Disclosed amount filter
    if disclosed_only:
        filtered = filtered[
            filtered["amount_disclosed"]
        ]

    # Startup search
    if startup_query:
        filtered = filtered[
            filtered["startup"]
            .str.contains(
                startup_query,
                case=False,
                na=False
            )
        ]

    return filtered