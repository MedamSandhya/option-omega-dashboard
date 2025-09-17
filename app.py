import streamlit as st
import pandas as pd

st.title("📊 Option Omega Strategy Dashboard")

tax_rate = st.number_input("Enter Tax Rate (%)", min_value=0.0, max_value=100.0, value=35.0, step=0.5)

example_trades = [
    {"strategy": "Iron Condor", "gross_pl": 2450},
    {"strategy": "Bull Put Spread", "gross_pl": 1890},
    {"strategy": "Call Credit Spread", "gross_pl": 3120},
    {"strategy": "Butterfly Spread", "gross_pl": 890},
    {"strategy": "Iron Butterfly", "gross_pl": 1650},
]

# Tax calculation directly in Streamlit
df = pd.DataFrame(example_trades)
df["tax_rate"] = tax_rate
df["tax_paid"] = df["gross_pl"].apply(lambda x: max(0, x * (tax_rate/100)) if x > 0 else 0)
df["net_pl"] = df["gross_pl"] - df["tax_paid"]

# Show metrics
cols = st.columns(len(df))
for idx, row in df.iterrows():
    with cols[idx]:
        st.metric(
            label=row["strategy"],
            value=f"${row['net_pl']:,.2f}",
            delta=f"Tax: ${row['tax_paid']:,.2f}"
        )

st.subheader("📋 Detailed Results")
st.dataframe(df.style.format({"gross_pl": "${:,.2f}", "tax_paid": "${:,.2f}", "net_pl": "${:,.2f}"}))

st.subheader("📊 Summary")
st.write(f"**Total Gross P/L:** ${df['gross_pl'].sum():,.2f}")
st.write(f"**Total Tax Paid:** ${df['tax_paid'].sum():,.2f}")
st.write(f"**Total Net P/L:** ${df['net_pl'].sum():,.2f}")