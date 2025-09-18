import streamlit as st
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide")

# === DARK/LIGHT MODE ===
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

# Define colors for light/dark
if dark_mode:
    bg_color = "#1e293b"
    card_color = "#0f172a"
    text_color = "#f1f5f9"
    accent = "#f97316"
else:
    bg_color = "#f8fafc"
    card_color = "white"
    text_color = "#111827"
    accent = "#f97316"

# === CUSTOM CSS ===
st.markdown(f"""
    <style>
    body, .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Inter', sans-serif;
    }}

    /* Navbar */
    .navbar {{
        position: sticky;
        top: 0;
        z-index: 100;
        background: linear-gradient(90deg, {accent}, #fb923c);
        padding: 18px 30px;
        border-radius: 0 0 14px 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .navbar-title {{
        font-size: 22px;
        font-weight: 800;
        color: white;
    }}
    .navbar-links span {{
        margin-left: 20px;
        cursor: pointer;
        font-weight: 500;
        color: white;
    }}
    .navbar-links span:hover {{
        text-decoration: underline;
    }}

    /* KPI Cards */
    .kpi-container {{
        display: flex;
        gap: 20px;
        margin: 25px 0;
    }}
    .kpi-card {{
        flex: 1;
        background: {card_color};
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.2s ease-in-out;
    }}
    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 700;
        color: #16a34a;
    }}
    .kpi-label {{
        font-size: 14px;
        color: #9ca3af;
    }}

    /* Data Table */
    .dataframe th {{
        background-color: {accent} !important;
        color: white !important;
        padding: 12px;
        text-align: center;
    }}
    .dataframe td {{
        text-align: center;
        padding: 10px;
    }}
    .dataframe tr:hover {{
        background-color: #fde68a !important;
    }}

    /* Download Button */
    .download-btn {{
        background: {accent};
        color: white;
        padding: 10px 20px;
        border-radius: 12px;
        font-weight: 600;
        text-decoration: none;
    }}
    .download-btn:hover {{
        background: #fb923c;
    }}
    </style>
""", unsafe_allow_html=True)

# === NAVBAR ===
st.markdown("""
<div class="navbar">
    <div class="navbar-title">📊 Option Omega</div>
    <div class="navbar-links">
        <span onclick="window.scrollTo(0, 300)">Dashboard</span>
        <span onclick="window.scrollTo(0, 800)">Strategies</span>
        <span onclick="window.scrollTo(0, document.body.scrollHeight)">About</span>
    </div>
</div>
""", unsafe_allow_html=True)

# === MAIN CONTENT ===
tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=30.0) / 100
uploaded_file = st.file_uploader("📂 Upload your Option Omega trade log (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    if "date_opened" in df.columns:
        df["date_opened"] = pd.to_datetime(df["date_opened"], errors="coerce")
        date_col = "date_opened"
    else:
        st.error("CSV must have 'Date Opened'")
        st.stop()

    min_date, max_date = df[date_col].min().date(), df[date_col].max().date()
    start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    df = df[(df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)]

    if "p/l" in df.columns:
        df.rename(columns={"p/l": "gross_pl"}, inplace=True)

    df["commissions_paid"] = df.get("opening_commissions_+_fees", 0) + df.get("closing_commissions_+_fees", 0)
    df["profit_after_commissions"] = df["gross_pl"] - df["commissions_paid"]

    summary = df.groupby("strategy").agg(
        Gross_PL=("profit_after_commissions", "sum"),
        Commissions=("commissions_paid", "sum")
    ).reset_index()

    summary["Tax_Paid"] = summary["Gross_PL"].apply(lambda x: x * tax_rate if x > 0 else 0)
    summary["Net_PL"] = summary["Gross_PL"] - summary["Commissions"] - summary["Tax_Paid"]

    # Totals
    total_gross, total_comm, total_tax, total_net = summary["Gross_PL"].sum(), summary["Commissions"].sum(), summary["Tax_Paid"].sum(), summary["Net_PL"].sum()

    # === KPI CARDS ===
    st.markdown("<div class='kpi-container'>", unsafe_allow_html=True)
    for value, label in [
        (total_gross, "Gross P/L"),
        (total_comm, "Commissions"),
        (total_tax, "Tax Paid"),
        (total_net, "Net P/L")
    ]:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>${value:,.2f}</div><div class='kpi-label'>{label}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # === STRATEGY TABLE ===
    st.markdown("## 📌 Strategy-Level Summary")
    st.dataframe(summary.style.format({
        "Gross_PL": "${:,.2f}",
        "Commissions": "${:,.2f}",
        "Tax_Paid": "${:,.2f}",
        "Net_PL": "${:,.2f}"
    }))

    # === DOWNLOAD BUTTON ===
    csv = summary.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Strategy Summary",
        data=csv,
        file_name="strategy_summary.csv",
        mime="text/csv",
        use_container_width=True
    )

# === ABOUT ===
st.markdown("## ℹ️ About")
st.write("This dashboard is built for analyzing Option Omega strategy performance with taxes, commissions, and net P/L in an intuitive interface.")