import streamlit as st
import pandas as pd
import base64

# === PAGE CONFIG ===
st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide", initial_sidebar_state="collapsed")

# ----------------------
# CUSTOM CSS (LIGHT MODE)
# ----------------------
st.markdown(
    """
    <style>
    /* ---------- General ---------- */
    :root{
      --bg: #f8fafc;
      --card: #ffffff;
      --muted: #6b7280;
      --accent: #f97316;
      --accent-2: #fb923c;
      --success: #16a34a;
      --text: #0f172a;
    }
    body, .stApp {
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }

    /* ---------- Navbar ---------- */
    .header {
      margin: 22px 40px;
      padding: 18px 28px;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
      border-radius: 14px;
      box-shadow: 0 6px 20px rgba(16,24,40,0.06);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand {
      display:flex;
      gap:12px;
      align-items:center;
      font-weight:800;
      color: white;
      font-size:20px;
    }
    .nav-links {
      display:flex;
      gap:22px;
      align-items:center;
    }
    .nav-links a {
      color: rgba(255,255,255,0.95);
      text-decoration: none;
      font-weight:600;
      cursor:pointer;
    }
    .nav-links a:hover { text-decoration: underline; }

    /* ---------- Page sections (cards) ---------- */
    .section {
      margin: 28px 40px;
      padding: 22px;
      background: var(--card);
      border-radius: 12px;
      box-shadow: 0 8px 22px rgba(15,23,42,0.04);
    }

    /* ---------- KPI Cards ---------- */
    .kpi-row {
      display:flex;
      gap:18px;
    }
    .kpi {
      flex:1;
      background: var(--card);
      border-radius:12px;
      padding:18px 20px;
      text-align:center;
      box-shadow: 0 6px 18px rgba(15,23,42,0.04);
      transition: transform .14s ease, box-shadow .14s ease;
    }
    .kpi:hover {
      transform: translateY(-6px);
      box-shadow: 0 12px 30px rgba(15,23,42,0.08);
    }
    .kpi .value { font-size:24px; font-weight:800; color: var(--success); }
    .kpi .label { color: var(--muted); margin-top:6px; font-size:13px; }

    /* ---------- Table styling ---------- */
    .dataframe th {
      background: var(--accent) !important;
      color: white !important;
      font-weight: 700;
      padding: 10px;
      text-align:center;
    }
    .dataframe td {
      padding: 10px;
      text-align:center;
      color: var(--text) !important;
    }
    .dataframe tr:nth-child(even) {
      background: #fffaf0 !important;
    }
    .dataframe tr:hover {
      background: #fff4e6 !important;
      transform: scale(1.001);
    }

    /* ---------- Download btn ---------- */
    .download-btn {
      display:inline-block;
      background: var(--accent);
      color: white;
      padding: 10px 16px;
      border-radius: 10px;
      font-weight:700;
      text-decoration:none;
      transition: transform .12s ease, background .12s ease;
    }
    .download-btn:hover { transform: translateY(-3px); background: #ea6f19; }

    /* ---------- Force light appearance for Streamlit inputs (important) ---------- */
    /* Covers most input types and file uploader elements */
    input[type="text"],
    input[type="number"],
    input[type="date"],
    .stTextInput > div > div > input,
    .stNumberInput input,
    .stDateInput input,
    textarea,
    .stSelectbox,
    .stFileUploader,
    .stFileUploader label,
    .stFileUploader div,
    .stFileUploader button,
    .stFileUploader input[type="file"]{
      background: #ffffff !important;
      color: var(--text) !important;
      border: 1px solid #e6e9ee !important;
      border-radius: 8px !important;
    }

    /* Ensure placeholder text visible */
    ::placeholder { color: #6b7280 !important; opacity: 1 !important; }

    /* Small responsive tweaks */
    @media (max-width: 900px) {
      .nav-links { display:none; }
      .header { padding: 14px; margin: 14px; }
      .section { margin: 14px; padding: 16px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------
# HEADER / NAVBAR
# ----------------------
st.markdown(
    """
    <div class="header">
      <div class="brand">
        <div style="width:28px;height:28px;border-radius:6px;background:white;display:flex;align-items:center;justify-content:center;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="7" width="3" height="10" fill="#4ADE80"/>
            <rect x="8" y="3" width="3" height="14" fill="#60A5FA"/>
            <rect x="13" y="11" width="3" height="6" fill="#F59E0B"/>
          </svg>
        </div>
        <div style="margin-left:8px">Option Omega</div>
      </div>

      <div class="nav-links">
        <a href="#dashboard">Dashboard</a>
        <a href="#strategies">Strategies</a>
        <a href="#about">About</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------
# INPUTS: tax + file upload + date range
# ----------------------
tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
tax_rate = tax_rate / 100.0

uploaded_file = st.file_uploader("📂 Upload your Option Omega trade log (CSV)", type="csv")

# If file uploaded, show date filter & process
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        st.stop()

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # --- determine date column ---
    date_col = None
    if "date_opened" in df.columns:
        df["date_opened"] = pd.to_datetime(df["date_opened"], errors="coerce")
        date_col = "date_opened"
    elif "exit_date" in df.columns:
        df["exit_date"] = pd.to_datetime(df["exit_date"], errors="coerce")
        date_col = "exit_date"
    else:
        st.error("CSV must contain 'Date Opened' or 'Exit Date' column.")
        st.stop()

    # Date range filter UI
    min_date = df[date_col].min().date()
    max_date = df[date_col].max().date()
    start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    # filter
    df = df[(df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)]

    # Normalize profit column
    if "p/l" in df.columns:
        df = df.rename(columns={"p/l": "gross_pl"})

    if "gross_pl" not in df.columns:
        st.error("CSV must contain a 'P/L' or 'Gross_PL' column.")
        st.stop()

    # Ensure commission columns exist
    if "opening_commissions_+_fees" not in df.columns:
        df["opening_commissions_+_fees"] = 0.0
    if "closing_commissions_+_fees" not in df.columns:
        df["closing_commissions_+_fees"] = 0.0

    # calculate commissions & profit after commissions
    df["commissions_paid"] = pd.to_numeric(df["opening_commissions_+_fees"], errors="coerce").fillna(0) + \
                             pd.to_numeric(df["closing_commissions_+_fees"], errors="coerce").fillna(0)

    # convert gross_pl numeric
    df["gross_pl"] = pd.to_numeric(df["gross_pl"], errors="coerce").fillna(0)

    df["profit_after_commissions"] = df["gross_pl"] - df["commissions_paid"]

    # group by strategy
    if "strategy" not in df.columns:
        st.error("CSV must contain a 'Strategy' column.")
        st.stop()

    summary = df.groupby("strategy").agg(
        Gross_PL=("profit_after_commissions", "sum"),
        Commissions=("commissions_paid", "sum")
    ).reset_index()

    # tax only on positive profits
    summary["Tax_Paid"] = summary["Gross_PL"].apply(lambda x: x * tax_rate if x > 0 else 0.0)
    # net PL = gross (after commissions) - tax  (we already subtracted commissions in profit_after_commissions)
    # Note: Gross_PL already is after commissions in our pipeline
    summary["Net_PL"] = summary["Gross_PL"] - summary["Tax_Paid"]

    # Totals
    total_gross = summary["Gross_PL"].sum()
    total_comm = summary["Commissions"].sum()
    total_tax = summary["Tax_Paid"].sum()
    total_net = summary["Net_PL"].sum()

    # ----------------------
    # DASHBOARD SECTION
    # ----------------------
    st.markdown('<div id="dashboard" class="section">', unsafe_allow_html=True)
    st.markdown("### 📊 Dashboard Overview")
    st.markdown(
        f"""
        <div class="kpi-row" style="margin-top:14px;">
          <div class="kpi"><div class="value">${total_gross:,.2f}</div><div class="label">Gross P/L</div></div>
          <div class="kpi"><div class="value">${total_comm:,.2f}</div><div class="label">Commissions</div></div>
          <div class="kpi"><div class="value">${total_tax:,.2f}</div><div class="label">Tax Paid</div></div>
          <div class="kpi"><div class="value">${total_net:,.2f}</div><div class="label">Net P/L</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------
    # STRATEGIES TABLE
    # ----------------------
    st.markdown('<div id="strategies" class="section">', unsafe_allow_html=True)
    st.markdown("### 📌 Strategy-Level Summary")
    st.write("Hover a row to highlight it. The Net P/L column is Gross (after commissions) minus tax.")
    # format currency
    formatted = summary.copy()
    formatted["Gross_PL"] = formatted["Gross_PL"].map(lambda x: f"${x:,.2f}")
    formatted["Commissions"] = formatted["Commissions"].map(lambda x: f"${x:,.2f}")
    formatted["Tax_Paid"] = formatted["Tax_Paid"].map(lambda x: f"${x:,.2f}")
    formatted["Net_PL"] = formatted["Net_PL"].map(lambda x: f"${x:,.2f}")

    st.dataframe(formatted, use_container_width=True)

    # download
    csv_bytes = summary.to_csv(index=False).encode("utf-8")
    b64 = base64.b64encode(csv_bytes).decode()
    st.markdown(f'<a class="download-btn" href="data:file/csv;base64,{b64}" download="strategy_summary.csv">⬇️ Download Strategy Summary</a>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------
    # ABOUT SECTION
    # ----------------------
    st.markdown('<div id="about" class="section">', unsafe_allow_html=True)
    st.markdown("### ℹ️ About")
    st.write(
        """
        This dashboard analyzes Option Omega trade logs and summarizes performance by strategy.
        - Upload your Option Omega CSV export.
        - Set a date range to focus the view.
        - Tax rate is applied to *positive* net profits.
        - Net P/L = (Gross after commissions) - Tax Paid.
        
        If you'd like:
        - I can add a small time-series chart for Gross P/L over time,
        - add row-level hover cards with a download button per strategy,
        - or add small icons to KPI cards for extra polish.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # no file uploaded: show a friendly empty state
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("### Upload your Option Omega CSV")
    st.write("Upload a CSV from Option Omega (must contain: Strategy, P/L or Gross_PL, Date Opened or Exit Date, Opening/Closing Commissions).")
    st.markdown("</div>", unsafe_allow_html=True)