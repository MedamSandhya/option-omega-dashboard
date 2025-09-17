import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Option Omega Dashboard", layout="wide")

st.title("📊 Option Omega Strategy Dashboard")

# 🔹 User input for tax rate
tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=35.0, step=0.5)

# 🔹 Example trades (later you can replace with CSV upload or API)
example_trades = [
    {"strategy": "Iron Condor", "gross_pl": 2450},
    {"strategy": "Bull Put Spread", "gross_pl": 1890},
    {"strategy": "Call Credit Spread", "gross_pl": 3120},
    {"strategy": "Butterfly Spread", "gross_pl": 890},
    {"strategy": "Iron Butterfly", "gross_pl": 1650},
]

# 🔹 Backend API call
backend_url = "http://127.0.0.1:8001/calculate_pl/"  # <- port 8001 since you started uvicorn with --port 8001
payload = {"trades": example_trades, "tax_rate": tax_rate}
response = requests.post(backend_url, json=payload)

if response.status_code == 200:
    trades = response.json()
    df = pd.DataFrame(trades)

    # Strategy metrics
    st.subheader("💰 Strategy Performance")
    cols = st.columns(len(df))
    for idx, row in df.iterrows():
        with cols[idx]:
            st.metric(
                label=row["strategy"],
                value=f"${row['net_pl']:,.2f}",
                delta=f"Tax: ${row['tax_paid']:,.2f}"
            )

    # Detailed table
    st.subheader("📋 Detailed Results")
    st.dataframe(
        df.style.format(
            {"gross_pl": "${:,.2f}", "tax_paid": "${:,.2f}", "net_pl": "${:,.2f}"}
        )
    )

    # Totals
    st.subheader("📊 Summary")
    total_gross = df["gross_pl"].sum()
    total_tax = df["tax_paid"].sum()
    total_net = df["net_pl"].sum()

    st.write(f"**Total Gross P/L:** ${total_gross:,.2f}")
    st.write(f"**Total Tax Paid:** ${total_tax:,.2f}")
    st.write(f"**Total Net P/L:** ${total_net:,.2f}")
else:
    st.error("Backend API call failed. Make sure FastAPI server is running.")