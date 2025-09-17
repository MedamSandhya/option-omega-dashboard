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

        # Normalize columns
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Ensure required columns
        if "p/l" not in df.columns or "strategy" not in df.columns:
            st.error("CSV must contain at least 'Strategy' and 'P/L' columns")
        else:
            # Rename and calculate commissions
            df = df.rename(columns={"p/l": "gross_pl"})
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

            # Net P/L after tax
            summary["Net_PL"] = summary["Gross_PL"] - summary["Tax_Paid"]

            # Reorder columns
            summary = summary[["strategy", "Gross_PL", "Commissions", "Tax_Paid", "Net_PL"]]

            # Show results
            st.subheader("📌 Strategy-Level Summary")
            st.dataframe(summary.style.format({
                "Gross_PL": "${:,.2f}",
                "Commissions": "${:,.2f}",
                "Tax_Paid": "${:,.2f}",
                "Net_PL": "${:,.2f}"
            }))

    except Exception as e:
        st.error(f"Error processing file: {e}")