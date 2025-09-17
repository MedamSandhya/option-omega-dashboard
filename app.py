import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide")

st.title("📊 Option Omega Strategy Dashboard")

# User input: tax rate
tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=35.0) / 100

# File uploader
uploaded_file = st.file_uploader("Upload your Option Omega trade log (CSV)", type="csv")

if uploaded_file is not None:
    try:
        # Read CSV
        df = pd.read_csv(uploaded_file)

        # Normalize column names
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Ensure we have a date column
        if "date_opened" in df.columns:
            df["date_opened"] = pd.to_datetime(df["date_opened"], errors="coerce")
            date_col = "date_opened"
        elif "exit_date" in df.columns:
            df["exit_date"] = pd.to_datetime(df["exit_date"], errors="coerce")
            date_col = "exit_date"
        else:
            st.error("CSV must contain a 'Date Opened' or 'Exit Date' column for filtering.")
            st.stop()

        # 🔹 Date filter inputs
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        start_date, end_date = st.date_input(
            "Select Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

        # Apply date filter
        mask = (df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)
        df = df.loc[mask]

        # Ensure required columns
        if "p/l" not in df.columns and "gross_pl" not in df.columns:
            st.error("CSV must contain at least 'Strategy' and 'P/L' (or Gross_PL) columns")
        else:
            # Rename if needed
            if "p/l" in df.columns:
                df = df.rename(columns={"p/l": "gross_pl"})

            # Handle commissions
            if "opening_commissions_+_fees" not in df.columns:
                df["opening_commissions_+_fees"] = 0
            if "closing_commissions_+_fees" not in df.columns:
                df["closing_commissions_+_fees"] = 0
            df["commissions_paid"] = df["opening_commissions_+_fees"] + df["closing_commissions_+_fees"]

            # Adjust profit by commissions
            df["profit_after_commissions"] = df["gross_pl"] - df["commissions_paid"]

            # Group by strategy
            summary = df.groupby("strategy").agg(
                Gross_PL=("profit_after_commissions", "sum"),
                Commissions=("commissions_paid", "sum")
            ).reset_index()

            # Tax (only if profit > 0)
            summary["Tax_Paid"] = summary["Gross_PL"].apply(lambda x: x * tax_rate if x > 0 else 0)

            # Net P/L after commissions AND tax
            summary["Net_PL"] = summary["Gross_PL"] - summary["Commissions"] - summary["Tax_Paid"]

            # Reorder columns
            summary = summary[["strategy", "Gross_PL", "Commissions", "Tax_Paid", "Net_PL"]]

            # 🔹 Overall totals
            total_gross = summary["Gross_PL"].sum()
            total_comm = summary["Commissions"].sum()
            total_tax = summary["Tax_Paid"].sum()
            total_net = summary["Net_PL"].sum()

            st.subheader("📊 Overall Dashboard")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Gross P/L", f"${total_gross:,.2f}")
            col2.metric("Commissions Paid", f"${total_comm:,.2f}")
            col3.metric("Tax Paid", f"${total_tax:,.2f}")
            col4.metric("Net P/L", f"${total_net:,.2f}")

            # 🔹 Show strategy-level results
            st.subheader("📌 Strategy-Level Summary")
            st.dataframe(summary.style.format({
                "Gross_PL": "${:,.2f}",
                "Commissions": "${:,.2f}",
                "Tax_Paid": "${:,.2f}",
                "Net_PL": "${:,.2f}"
            }))

    except Exception as e:
        st.error(f"Error processing file: {e}")