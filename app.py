import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Options Strategy Dashboard", layout="wide")

st.title("📊 Option Omega Strategy Dashboard")

uploaded_file = st.file_uploader("Upload your Option Omega Trade Log CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]

    if 'Open Date' in df.columns:
        df['Open Date'] = pd.to_datetime(df['Open Date'])

    strategy_names = df['Strategy'].dropna().unique()
    selected_strategies = st.sidebar.multiselect("Filter by Strategy", strategy_names, default=list(strategy_names))
    df_filtered = df[df['Strategy'].isin(selected_strategies)]

    st.subheader("🔍 Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Trades", len(df_filtered))
    with col2:
        st.metric("Total P/L", f"${df_filtered['P/L'].sum():,.2f}")
    with col3:
        st.metric("Win Rate", f"{(df_filtered['P/L'] > 0).mean() * 100:.2f}%")

    if 'Open Date' in df_filtered.columns:
        pl_df = df_filtered.groupby('Open Date')['P/L'].sum().cumsum().reset_index()
        fig = px.line(pl_df, x='Open Date', y='P/L', title="📈 Cumulative P/L Over Time")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📆 Monthly P/L")
    if 'Open Date' in df_filtered.columns:
        df_filtered['Month'] = df_filtered['Open Date'].dt.to_period('M').astype(str)
        monthly = df_filtered.groupby('Month')['P/L'].sum().reset_index()
        fig = px.bar(monthly, x='Month', y='P/L', title="Monthly Profit/Loss", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Strategy Breakdown")
    strategy_table = df_filtered.groupby('Strategy').agg({
        'P/L': ['sum', 'mean', 'count']
    })
    strategy_table.columns = ['Total P/L', 'Avg P/L', 'Trades']
    st.dataframe(strategy_table.sort_values("Total P/L", ascending=False))

    st.download_button("Download Filtered CSV", data=df_filtered.to_csv(index=False), file_name="filtered_trade_log.csv")

else:
    st.info("Upload a CSV file to see strategy insights.")
