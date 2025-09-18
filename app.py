import streamlit as st
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide")

# === CUSTOM CSS ===
st.markdown("""
    <style>
    body, .stApp {
        font-family: 'Poppins', sans-serif;
        background-color: #f9fafb;
        color: #111827;
    }

    /* Navbar */
    .navbar {
        background: #ffffff;
        padding: 18px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .navbar-title {
        font-size: 24px;
        font-weight: 800;
        color: #f97316;
    }
    .navbar-links {
        color: #f97316;
        font-weight: 600;
        margin-left: 20px;
        cursor: pointer;
    }

    /* KPI Cards */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 25px;
    }
    .kpi-card {
        flex: 1;
        background: white;
        padding: 25px;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        margin: 0 10px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 6px;
        color: #16a34a;
    }
    .kpi-label {
        font-size: 14px;
        color: #6b7280;
    }

    /* File uploader */
    .uploadedFile { 
        background: #ffffff !important; 
        color: #111827 !important; 
    }

    /* Tax input */
    div[data-baseweb="input"] > div {
        background-color: #ffedd5 !important;
        border-radius: 8px !important;
    }
    input {
        color: #111827 !important;
    }

    /* Section Titles */
    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin: 30px 0 15px 0;
        padding-bottom: 8px;
        border-bottom: 3px solid #f97316;
        color: #f97316;
    }

    /* Data Table */
    .dataframe th {
        background-color: #f97316 !important;
        color: white !important;
        text-align: center;
        font-size: 14px;
        padding: 10px;
    }
    .dataframe td {
        text-align: center;
        padding: 10px;
    }
    .dataframe tr:hover {
        background-color: #fff7ed !important;
    }

    /* Download Button */
    .download-btn {
        background: #fb923c;
        color: white !important;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 10px;
        border: none;
        text-decoration: none !important;
        display: inline-block;
        margin-top: 20px;
    }
    .download-btn:hover {
        background: #f97316;
        text-decoration: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# === NAVBAR ===
st.markdown("""
<div class="navbar">
    <div class="navbar-title">📊 Option Omega</div>
    <div>
        <span class="navbar-links">Dashboard</span>
        <span class="navbar-links">Strategies</span>
    </div>
</div>
""", unsafe_allow_html=True)

# === INPUTS ===
tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=30.0) / 100
uploaded_file = st.file_uploader("📂 Upload your Option Omega trade log (CSV)", type="csv", label_visibility="collapsed")

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
        start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
        df = df[(df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)]

        # Normalize columns
        if "p/l" in df.columns:
            df = df.rename(columns={"p/l": "gross_pl"})
        if "gross_pl" not in df.columns:
            st.error("CSV must contain 'P/L' or 'Gross_PL'")
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

        # === DASHBOARD OVERVIEW ===
        st.markdown("<div class='section-title'>📊 Dashboard Overview</div>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_gross:,.2f}</div><div class='kpi-label'>Gross P/L</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_comm:,.2f}</div><div class='kpi-label'>Commissions</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_tax:,.2f}</div><div class='kpi-label'>Tax Paid</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_net:,.2f}</div><div class='kpi-label'>Net P/L</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # === STRATEGY SUMMARY ===
        st.markdown("<div class='section-title'>📌 Strategy Performance Summary</div>", unsafe_allow_html=True)
        st.dataframe(summary.style.format({
            "Gross_PL": "${:,.2f}",
            "Commissions": "${:,.2f}",
            "Tax_Paid": "${:,.2f}",
            "Net_PL": "${:,.2f}"
        }))

        # Download button
        csv = summary.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Strategy Summary",
            data=csv,
            file_name="strategy_summary.csv",
            mime="text/csv",
            key="download-csv",
            use_container_width=True,
            type="primary"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")