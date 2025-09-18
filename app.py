import streamlit as st
import pandas as pd
import base64

# === PAGE CONFIG ===
st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide")

# === CUSTOM CSS ===
st.markdown("""
    <style>
    body, .stApp {
        font-family: 'Poppins', sans-serif;
        background-color: #f8fafc;
        color: #111827;
    }

    /* Navbar */
    .navbar {
        background: linear-gradient(90deg, #f97316, #fb923c);
        padding: 18px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }
    .navbar-title {
        font-size: 24px;
        font-weight: 800;
        color: white;
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
        transition: all 0.2s ease-in-out;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
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

    /* Strategy Table */
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
    .dataframe tr {
        transition: all 0.2s ease-in-out;
    }
    .dataframe tr:hover {
        background-color: #fde68a !important;
        transform: scale(1.01);
    }

    /* Download Button */
    .download-btn {
        display: inline-block;
        padding: 12px 22px;
        margin: 15px 0;
        background-color: #f97316;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        text-decoration: none;
        transition: all 0.3s ease-in-out;
    }
    .download-btn:hover {
        background-color: #ea580c;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# === NAVBAR with real navigation ===
st.markdown("<div class='navbar'><div class='navbar-title'>📊 Option Omega Strategy Dashboard</div></div>", unsafe_allow_html=True)
page = st.radio("", ["Dashboard", "Strategies", "About"], horizontal=True)

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

        # === PAGE ROUTING ===
        if page == "Dashboard":
            st.markdown("<div class='kpi-container'>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_gross:,.2f}</div><div class='kpi-label'>Gross P/L</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_comm:,.2f}</div><div class='kpi-label'>Commissions</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_tax:,.2f}</div><div class='kpi-label'>Tax Paid</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_net:,.2f}</div><div class='kpi-label'>Net P/L</div></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        elif page == "Strategies":
            st.markdown("### 📌 Strategy-Level Summary")

            # Download CSV button
            csv_export = summary.to_csv(index=False).encode("utf-8")
            b64 = base64.b64encode(csv_export).decode()
            st.markdown(f"<a class='download-btn' href='data:file/csv;base64,{b64}' download='strategy_summary.csv'>⬇ Download CSV</a>", unsafe_allow_html=True)

            st.dataframe(summary.style.format({
                "Gross_PL": "${:,.2f}",
                "Commissions": "${:,.2f}",
                "Tax_Paid": "${:,.2f}",
                "Net_PL": "${:,.2f}"
            }))

        elif page == "About":
            st.subheader("ℹ️ About This Dashboard")
            st.markdown("""
            This dashboard is built for **Option Omega traders** to analyze performance across strategies.  
            - Upload your trade logs (CSV).  
            - See both **overall results** and **strategy-level breakdowns**.  
            - Track **Gross P/L, Commissions, Taxes, Net P/L** over any date range.  

            Designed with ❤️ to help traders make data-driven decisions.
            """)
    except Exception as e:
        st.error(f"Error processing file: {e}")