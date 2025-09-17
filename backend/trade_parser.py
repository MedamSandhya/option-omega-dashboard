import pandas as pd

def parse_trade_log(file_path: str) -> pd.DataFrame:
    """
    Load and parse the Option Omega trade log CSV file.
    Normalize column names and ensure required fields exist.
    """
    df = pd.read_csv(file_path)

    # Normalize column names to lowercase with underscores
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Rename important columns for consistency
    if "p/l" in df.columns:
        df = df.rename(columns={"p/l": "gross_pl"})
    if "strategy" not in df.columns:
        raise ValueError("CSV must contain a 'Strategy' column")

    # Add missing commission columns if not present
    if "opening_commissions_+_fees" not in df.columns:
        df["opening_commissions_+_fees"] = 0
    if "closing_commissions_+_fees" not in df.columns:
        df["closing_commissions_+_fees"] = 0

    # Calculate total commissions
    df["commissions_paid"] = df["opening_commissions_+_fees"] + df["closing_commissions_+_fees"]

    return df


def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter trades between start and end date using 'date_closed'.
    """
    if "date_closed" not in df.columns:
        raise ValueError("CSV must contain a 'Date Closed' column")

    df["date_closed"] = pd.to_datetime(df["date_closed"])
    return df[(df["date_closed"] >= pd.to_datetime(start_date)) & 
              (df["date_closed"] <= pd.to_datetime(end_date))]


def calculate_strategy_summary(df: pd.DataFrame, tax_rate: float = 0.15) -> pd.DataFrame:
    """
    Summarize trades grouped by strategy:
    - Gross Profit/Loss (after commissions)
    - Commissions Paid
    - Tax Paid (applied only to positive profits)
    - Net P/L (after tax)
    """
    # Ensure gross_pl exists
    if "gross_pl" not in df.columns:
        raise ValueError("CSV must contain a 'P/L' column")

    # Adjust profit by commissions
    df["profit_after_commissions"] = df["gross_pl"] - df["commissions_paid"]

    # Group by strategy
    summary = df.groupby("strategy").agg(
        Gross_PL=("profit_after_commissions", "sum"),
        Commissions=("commissions_paid", "sum")
    ).reset_index()

    # Apply tax only if profit is positive
    summary["Tax_Paid"] = summary["Gross_PL"].apply(lambda x: x * tax_rate if x > 0 else 0)

    # Net P/L = Gross (after commissions) - Tax
    summary["Net_PL"] = summary["Gross_PL"] - summary["Tax_Paid"]

    return summary[["strategy", "Gross_PL", "Commissions", "Tax_Paid", "Net_PL"]]