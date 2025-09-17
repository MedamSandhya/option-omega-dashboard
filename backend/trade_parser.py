import pandas as pd

def parse_trade_log(file_path: str) -> pd.DataFrame:
    """
    Load and parse the trade log CSV file from Option Omega.
    Normalizes column names and ensures required fields exist.
    """
    df = pd.read_csv(file_path)

    # Normalize column names (lowercase, underscores)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Map Option Omega columns to standardized names
    if "p/l" in df.columns:
        df = df.rename(columns={"p/l": "gross_pl"})
    if "strategy" not in df.columns:
        raise ValueError("CSV must contain a 'Strategy' column")

    # Fill NaN values for commissions if missing
    if "opening_commissions_+_fees" not in df.columns:
        df["opening_commissions_+_fees"] = 0
    if "closing_commissions_+_fees" not in df.columns:
        df["closing_commissions_+_fees"] = 0

    return df


def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter trades between start and end date.
    Uses 'date_closed' column from Option Omega export.
    """
    if "date_closed" not in df.columns:
        raise ValueError("CSV must contain a 'Date Closed' column")
    
    df["date_closed"] = pd.to_datetime(df["date_closed"])
    return df[(df["date_closed"] >= pd.to_datetime(start_date)) & 
              (df["date_closed"] <= pd.to_datetime(end_date))]


def calculate_strategy_summary(df: pd.DataFrame, tax_rate: float = 0.15) -> pd.DataFrame:
    """
    Summarize trades grouped by strategy:
    - Gross P/L (after fees)
    - Tax (applied only on positive profits)
    - Net P/L
    """
    # Ensure gross_pl exists
    if "gross_pl" not in df.columns:
        raise ValueError("CSV must contain a 'P/L' column")

    # Compute total fees (opening + closing)
    df["total_fees"] = df["opening_commissions_+_fees"] + df["closing_commissions_+_fees"]

    # Adjust P/L by subtracting fees
    df["gross_after_fees"] = df["gross_pl"] - df["total_fees"]

    # Group by strategy
    summary = df.groupby("strategy").agg(
        Trades=("strategy", "count"),
        Gross_PL=("gross_after_fees", "sum")
    ).reset_index()

    # Apply tax only to profitable strategies
    summary["Tax"] = summary["Gross_PL"].apply(lambda x: x * tax_rate if x > 0 else 0)

    # Net P/L after tax
    summary["Net_PL"] = summary["Gross_PL"] - summary["Tax"]

    return summary