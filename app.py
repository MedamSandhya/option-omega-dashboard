import streamlit as st
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide")

# === GLOBAL CSS ===
st.markdown("""
    <style>
    /* Global Font & Background */
    body, .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #f9fafb;
    }
    /* Header */
    .header {
        background: linear-gradient(90deg, #f97316, #fb923c);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
    }
    .header-title {
        font-size: 34px;
        font-weight: 800;
        color: white;
    }
    .header-sub {
        font-size: 16px;
        color: #fef3c7;
    }
    /* KPI Cards */
    .kpi-card {
        background: white;
        padding: 25px;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.2s ease-in-out;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #16a34a;
        margin-bottom: 6px;
    }
    .kpi-label {
        font-size: 14px;
        color: #6b7280;
    }
    /* Data Table */
    .dataframe th {
        background-color: #f97316 !important;
        color: white !important;
        text-align: center !important;
        padding: 10px;
    }
    .dataframe td {
        padding: 10px;
        text-align: center;
    }
    .dataframe tr:nth-child(even) {
        background-color: #fef9f6 !important;
    }
    .dataframe tr:hover {
        background-color: #fef3c7 !important;
    }
    </style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("""
<div class="header">
    <div class="header-title">Option Omega Strategy Dashboard</div>
    <div class="header-sub">Professional Options Strategy Performance Analytics</div>
</div>
""", unsafe_allow_html=True)

# === INPUTS ===
tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=30.0) / 100
uploaded_file = st.file_uploader("📂 Upload your Option Omega trade log (CSV)", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Handle dates
        if "date_opened" in df.columns:
            df["date_opened"] = pd.to_datetime(df["date_opened"], errors="coerce")
            date_col = "date_opened"
        elif "exit_date" in df.columns:
            df["exit_date"] = pd.to_datetime(df["exit_date"], errors="coerce")
            date_col = "exit_date"
        else:
            st.error("CSV must contain a 'Date Opened' or 'Exit Date' column")
            st.stop()

        # Date filter
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        start_date, end_date = st.date_input(
            "Select Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        mask = (df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)
        df = df.loc[mask]

        # Normalize columns
        if "p/l" in df.columns:
            df = df.rename(columns={"p/l": "gross_pl"})
        if "gross_pl" not in df.columns:
            st.error("CSV must contain a 'P/L' or 'Gross_PL' column")
            st.stop()

        if "opening_commissions_+_fees" not in df.columns:
            df["opening_commissions_+_fees"] = 0
        if "closing_commissions_+_fees" not in df.columns:
            df["closing_commissions_+_fees"] = 0

        df["commissions_paid"] = df["opening_commissions_+_fees"] + df["closing_commissions_+_fees"]
        df["profit_after_commissions"] = df["gross_pl"] - df["commissions_paid"]

        summary = df.groupby("strategy").agg(
            Gross_PL=("profit_after_commissions", "sum"),
            Commissions=("commissions_paid", "sum")
        ).reset_index()

        summary["Tax_Paid"] = summary["Gross_PL"].apply(lambda x: x * tax_rate if x > 0 else 0)
        summary["Net_PL"] = summary["Gross_PL"] - summary["Commissions"] - summary["Tax_Paid"]

        # Totals
        total_gross = summary["Gross_PL"].sum()
        total_comm = summary["Commissions"].sum()
        total_tax = summary["Tax_Paid"].sum()
        total_net = summary["Net_PL"].sum()

        # === KPI CARDS ===
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_gross:,.2f}</div><div class='kpi-label'>Gross P/L</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_comm:,.2f}</div><div class='kpi-label'>Commissions</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_tax:,.2f}</div><div class='kpi-label'>Tax Paid</div></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_net:,.2f}</div><div class='kpi-label'>Net P/L</div></div>", unsafe_allow_html=True)

        # === TABLE ===
        st.markdown("### 📌 Strategy-Level Summary")
        st.dataframe(summary.style.format({
            "Gross_PL": "${:,.2f}",
            "Commissions": "${:,.2f}",
            "Tax_Paid": "${:,.2f}",
            "Net_PL": "${:,.2f}"
        }))

    except Exception as e:
        st.error(f"Error processing file: {e}")