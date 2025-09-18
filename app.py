import streamlit as st
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide")

# === CUSTOM CSS ===
st.markdown("""
    <style>
    body, .stApp {
        font-family: 'Poppins', sans-serif;
        background-color: #f3f4f6;
        color: #111827;
    }

    /* Force all input widgets to white */
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stFileUploaderDropzone"],
    div[data-testid="stDateInput"] input {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1.5px solid #e5e7eb !important;
        border-radius: 10px !important;
        font-size: 14px !important;
        padding: 8px 12px !important;
    }

    /* File uploader dropzone */
    div[data-testid="stFileUploaderDropzone"] {
        background: #ffffff !important;
        border: 2px dashed #f97316 !important;
        border-radius: 14px !important;
        color: #374151 !important;
        text-align: center;
        padding: 20px;
    }
    div[data-testid="stFileUploaderDropzone"] p {
        color: #f97316 !important;
        font-weight: 600 !important;
    }

    /* Date input container */
    div[data-testid="stDateInput"] {
        background: #ffffff !important;
        border-radius: 10px !important;
        padding: 6px;
    }

    /* Number input container */
    div[data-testid="stNumberInput"] {
        background: #ffffff !important;
        border-radius: 10px !important;
        padding: 6px;
    }

    /* KPI cards */
    .kpi-card {
        flex: 1;
        background: #ffffff;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        margin: 0 12px;
    }

    /* Section white card */
    .section-card {
        background: #ffffff;
        padding: 28px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
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

# === INPUTS SECTION ===
with st.container():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=30.0) / 100
    with col2:
        uploaded_file = st.file_uploader("📂 Upload your Option Omega trade log (CSV)", type="csv")
    st.markdown("</div>", unsafe_allow_html=True)

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
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
        st.markdown("</div>", unsafe_allow_html=True)
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

        # === KPI CARDS ===
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Dashboard Overview</div>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_gross:,.2f}</div><div class='kpi-label'>Gross P/L</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_comm:,.2f}</div><div class='kpi-label'>Commissions</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_tax:,.2f}</div><div class='kpi-label'>Tax Paid</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_net:,.2f}</div><div class='kpi-label'>Net P/L</div></div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

        # === STRATEGY SUMMARY ===
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Strategy Performance Summary</div>", unsafe_allow_html=True)
        st.dataframe(summary.style.format({
            "Gross_PL": "${:,.2f}",
            "Commissions": "${:,.2f}",
            "Tax_Paid": "${:,.2f}",
            "Net_PL": "${:,.2f}"
        }))
        st.markdown("</div>", unsafe_allow_html=True)

        # === DOWNLOAD BUTTON ===
        st.download_button(
            label="Download Strategy Summary",
            data=summary.to_csv(index=False).encode("utf-8"),
            file_name="strategy_summary.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")