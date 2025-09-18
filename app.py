import streamlit as st
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide")

# === GLOBAL CSS FIX ===
st.markdown("""
    <style>
    body, .stApp {
        font-family: 'Poppins', sans-serif;
        background-color: #f3f4f6; /* light gray page background */
        color: #111827;
    }

    /* White card containers */
    .card {
        background: #ffffff;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 25px;
    }

    /* Navbar */
    .navbar {
        background: #ffffff;
        padding: 16px 28px;
        border-radius: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }
    .navbar-title {
        font-size: 22px;
        font-weight: 800;
        color: #fb923c;
    }
    .navbar-links {
        font-size: 16px;
        font-weight: 600;
        margin-left: 20px;
        cursor: pointer;
        color: #374151;
        text-decoration: none;
    }
    .navbar-links:hover {
        color: #f97316;
    }

    /* Inputs & uploader force light theme */
    .stTextInput, .stNumberInput, .stDateInput, .stFileUploader {
        background-color: #ffffff !important;
        color: #111827 !important;
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        padding: 10px;
    }
    input, textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    .stFileUploader label {
        color: #f97316 !important;
        font-weight: 600 !important;
    }

    /* Section titles */
    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin: 10px 0 20px 0;
        color: #fb923c;
    }

    /* KPI cards */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
    }
    .kpi-card {
        flex: 1;
        background: #ffffff;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 6px;
        color: #16a34a;
    }
    .kpi-label {
        font-size: 14px;
        font-weight: 500;
        color: #6b7280;
    }

    /* Data table */
    .dataframe th {
        background-color: #f97316 !important;
        color: white !important;
        text-align: center;
    }
    .dataframe td {
        text-align: center;
    }
    .dataframe tr:hover {
        background-color: #fff7ed !important;
    }

    /* Download button */
    .stDownloadButton button {
        background: #fb923c;
        color: white !important;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 10px;
        border: none;
    }
    .stDownloadButton button:hover {
        background: #f97316;
    }

    /* Remove empty white bars */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    </style>
""", unsafe_allow_html=True)


# === NAVBAR ===
st.markdown("""
<div class="navbar">
    <div class="navbar-title">Smart Tax</div>
    <div>
        <a class="navbar-links" href="#dashboard">Dashboard</a>
        <a class="navbar-links" href="#strategies">Strategies</a>
    </div>
</div>
""", unsafe_allow_html=True)

# === INPUT SECTION ===
with st.container():
    col1, col2 = st.columns([1, 2])
    with col1:
        tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=30.0) / 100
    with col2:
        uploaded_file = st.file_uploader("Upload your Option Omega CSV trade log", type="csv")

# === PROCESS CSV ===
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Date handling
        if "date_opened" in df.columns:
            df["date_opened"] = pd.to_datetime(df["date_opened"], errors="coerce")
            date_col = "date_opened"
        elif "exit_date" in df.columns:
            df["exit_date"] = pd.to_datetime(df["exit_date"], errors="coerce")
            date_col = "exit_date"
        else:
            st.error("CSV must contain 'Date Opened' or 'Exit Date'")
            st.stop()

        # Date filter
        min_date, max_date = df[date_col].min().date(), df[date_col].max().date()
        start_date, end_date = st.date_input("Select Date Range", [min_date, max_date],
                                             min_value=min_date, max_value=max_date)
        df = df[(df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)]

        # Normalize P/L
        if "p/l" in df.columns:
            df.rename(columns={"p/l": "gross_pl"}, inplace=True)
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
        total_gross, total_comm, total_tax, total_net = (
            summary["Gross_PL"].sum(),
            summary["Commissions"].sum(),
            summary["Tax_Paid"].sum(),
            summary["Net_PL"].sum(),
        )

        # === DASHBOARD SECTION ===
        st.markdown("<div id='dashboard'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'><div class='section-title'>Dashboard Overview</div>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-container'>", unsafe_allow_html=True)
        for val, label in [
            (total_gross, "Gross P/L"),
            (total_comm, "Commissions"),
            (total_tax, "Tax Paid"),
            (total_net, "Net P/L"),
        ]:
            st.markdown(
                f"<div class='kpi-card'><div class='kpi-value'>${val:,.2f}</div><div class='kpi-label'>{label}</div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div></div>", unsafe_allow_html=True)

        # === STRATEGIES SECTION ===
        st.markdown("<div id='strategies'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'><div class='section-title'>Strategy Performance Summary</div>", unsafe_allow_html=True)
        st.dataframe(summary.style.format({
            "Gross_PL": "${:,.2f}",
            "Commissions": "${:,.2f}",
            "Tax_Paid": "${:,.2f}",
            "Net_PL": "${:,.2f}"
        }))
        csv = summary.to_csv(index=False).encode("utf-8")
        st.download_button("Download", csv, "strategy_summary.csv", "text/csv")
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")