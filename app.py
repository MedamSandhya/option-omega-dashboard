import streamlit as st
import pandas as pd
import base64

# === PAGE CONFIG ===
st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide")

# === MODE TOGGLE ===
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = mode

# === THEME CSS ===
light_theme = """
:root {
    --bg: #f9fafb;
    --card: #ffffff;
    --text: #111827;
    --muted: #6b7280;
    --accent: #f97316;
    --success: #16a34a;
}
"""

dark_theme = """
:root {
    --bg: #1e293b;
    --card: #0f172a;
    --text: #f8fafc;
    --muted: #94a3b8;
    --accent: #fb923c;
    --success: #22c55e;
}
"""

theme = dark_theme if st.session_state.dark_mode else light_theme

st.markdown(f"""
<style>
{theme}

body, .stApp {{
    background-color: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}}

.navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 30px;
    margin-bottom: 30px;
    background: var(--card);
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    position: sticky;
    top: 0;
    z-index: 10;
}}
.navbar-title {{
    font-size: 22px;
    font-weight: 800;
    color: var(--accent);
}}
.navbar-links a {{
    margin-left: 25px;
    font-weight: 500;
    cursor: pointer;
    color: var(--text);
    text-decoration: none;
}}
.navbar-links a:hover {{
    color: var(--accent);
}}

.section {{
    margin: 50px 0;
    padding: 30px;
    background: var(--card);
    border-radius: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.06);
}}

.kpi-container {{
    display: flex;
    justify-content: space-around;
    margin-top: 20px;
}}
.kpi-card {{
    flex: 1;
    margin: 0 12px;
    background: var(--card);
    border-radius: 14px;
    padding: 25px;
    text-align: center;
    box-shadow: 6px 6px 12px rgba(0,0,0,0.06);
    transition: all 0.2s ease-in-out;
}}
.kpi-card:hover {{
    transform: translateY(-6px);
}}
.kpi-value {{
    font-size: 28px;
    font-weight: bold;
    color: var(--success);
}}
.kpi-label {{
    font-size: 14px;
    color: var(--muted);
}}

.dataframe tr:hover {{
    background-color: rgba(249, 115, 22, 0.1) !important;
    transform: scale(1.01);
}}

.download-btn {{
    display: inline-block;
    padding: 10px 20px;
    margin: 15px 0;
    background-color: var(--accent);
    color: white;
    font-weight: bold;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.2s ease;
}}
.download-btn:hover {{
    background-color: #ea580c;
    transform: scale(1.05);
}}
</style>
""", unsafe_allow_html=True)

# === NAVBAR ===
st.markdown("""
<div class="navbar">
  <div class="navbar-title">📊 Option Omega</div>
  <div class="navbar-links">
    <a href="#dashboard">Dashboard</a>
    <a href="#strategies">Strategies</a>
    <a href="#about">About</a>
  </div>
</div>
""", unsafe_allow_html=True)

# === INPUTS ===
tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=30.0) / 100
uploaded_file = st.file_uploader("📂 Upload your Option Omega trade log (CSV)", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

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

        # === Dashboard Section ===
        st.markdown('<div class="section" id="dashboard">', unsafe_allow_html=True)
        st.subheader("📊 Dashboard Overview")
        st.markdown("<div class='kpi-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_gross:,.2f}</div><div class='kpi-label'>Gross P/L</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_comm:,.2f}</div><div class='kpi-label'>Commissions</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_tax:,.2f}</div><div class='kpi-label'>Tax Paid</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${total_net:,.2f}</div><div class='kpi-label'>Net P/L</div></div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

        # === Strategies Section ===
        st.markdown('<div class="section" id="strategies">', unsafe_allow_html=True)
        st.subheader("📌 Strategy-Level Summary")
        csv_export = summary.to_csv(index=False).encode("utf-8")
        b64 = base64.b64encode(csv_export).decode()
        st.markdown(f"<a class='download-btn' href='data:file/csv;base64,{b64}' download='strategy_summary.csv'>⬇ Download CSV</a>", unsafe_allow_html=True)
        st.dataframe(summary.style.format({
            "Gross_PL": "${:,.2f}",
            "Commissions": "${:,.2f}",
            "Tax_Paid": "${:,.2f}",
            "Net_PL": "${:,.2f}"
        }))
        st.markdown("</div>", unsafe_allow_html=True)

        # === About Section ===
        st.markdown('<div class="section" id="about">', unsafe_allow_html=True)
        st.subheader("ℹ️ About This Dashboard")
        st.markdown("""
        This dashboard is built to analyze **options trading strategies** like a pro.  
        ✅ Upload your trade logs  
        ✅ Adjust tax rate & commissions  
        ✅ See live gross/net performance  
        ✅ Export results anytime  

        Designed with a modern, professional look — with both **light and dark modes**.
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")