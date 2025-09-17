import streamlit as st
import pandas as pd

st.set_page_config(page_title="Option Omega Strategy Dashboard", layout="wide")

st.title("📊 Option Omega Strategy Dashboard")

# 🔹 User input for tax rate
tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=35.0, step=0.5)

# 🔹 File uploader
uploaded_file = st.file_uploader("Upload your Option Omega trade log (CSV)", type=["csv"])

if uploaded_file is not None:
    # Read CSV into DataFrame
    df = pd.read_csv(uploaded_file)

    st.write("📋 Preview of uploaded CSV:")
    st.dataframe(df.head())

    # Let user choose which columns map to strategy and P/L
    strategy_col = st.selectbox("Select Strategy Column", df.columns)
    pl_col = st.selectbox("Select Gross P/L Column", df.columns)

    # Rename for consistency
    df = df.rename(columns={strategy_col: "strategy", pl_col: "gross_pl"})

    # Apply tax calculations
    df["tax_rate"] = tax_rate
    df["tax_paid"] = df["gross_pl"].apply(lambda x: max(0, x * (tax_rate / 100)) if x > 0 else 0)
    df["net_pl"] = df["gross_pl"] - df["tax_paid"]

    # Show strategy performance
    st.subheader("💰 Strategy Performance")
    cols = st.columns(min(len(df), 5))  # limit to 5 per row
    for idx, row in df.iterrows():
        with cols[idx % 5]:
            st.metric(
                label=row["strategy"],
                value=f"${row['net_pl']:,.2f}",
                delta=f"Tax: ${row['tax_paid']:,.2f}"
            )

    # Detailed results
    st.subheader("📋 Detailed Results")
    st.dataframe(
        df.style.format({"gross_pl": "${:,.2f}", "tax_paid": "${:,.2f}", "net_pl": "${:,.2f}"})
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
    st.info("Please upload a trade log CSV to see results.")