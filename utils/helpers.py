import pandas as pd
import numpy as np

def clean_data(filepath="data/indian_startup_funding.csv"):
    """
    Load and clean the Indian Startup Funding dataset.

    Returns:
        df (pd.DataFrame): Cleaned dataset
        report (dict): Summary of cleaning operations
    """

    # Load dataset
    raw_df = pd.read_csv(filepath)
    raw_df.columns = raw_df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = raw_df.copy()

    report = {}
    report["initial_rows"] = len(df)

    # Handle missing values
    df = df.dropna(subset=["startup_name", "industry", "amount_in_usd", "date"])
    if "investors" in df.columns:
        df["investors"] = df["investors"].fillna("Undisclosed")
    report["missing_values_handled"] = raw_df.isna().sum().to_dict()

    # Convert types
    df["amount_in_usd"] = pd.to_numeric(df["amount_in_usd"], errors="coerce")
    df = df.dropna(subset=["amount_in_usd"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # Remove duplicates
    report["duplicates_removed"] = raw_df.duplicated().sum()
    df = df.drop_duplicates()

    # Extract year and month
    if "year" not in df.columns:
        df["year"] = df["date"].dt.year
    if "month" not in df.columns:
        df["month"] = df["date"].dt.month

    # Final report
    report["final_rows"] = len(df)
    report["rows_dropped"] = report["initial_rows"] - report["final_rows"]

    return df, report
