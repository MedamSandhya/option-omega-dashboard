import pandas as pd

def parse_trade_log(file_path: str) -> pd.DataFrame:
    """
    Load and parse the trade log CSV file.
    """
    df = pd.read_csv(file_path)
    df['Entry Date'] = pd.to_datetime(df['Entry Date'])
    df['Exit Date'] = pd.to_datetime(df['Exit Date'])
    return df

def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter trades between start and end date.
    """
    return df[(df['Exit Date'] >= pd.to_datetime(start_date)) & (df['Exit Date'] <= pd.to_datetime(end_date))]

import pandas as pd

def calculate_strategy_summary(df: pd.DataFrame, tax_rate: float = 0.15) -> pd.DataFrame:
    df['Gross P/L'] = df['Exit Price'] - df['Entry Price']
    
    # Group by strategy and calculate gross profit
    summary = df.groupby('Strategy').agg(
        Trades=('Strategy', 'count'),
        Gross_PL=('Gross P/L', 'sum')
    ).reset_index()
    
    # Calculate tax (only on positive profits)
    summary['Tax'] = summary['Gross_PL'].apply(lambda x: x * tax_rate if x > 0 else 0)
    
    # Net P/L = Gross - Tax
    summary['Net_PL'] = summary['Gross_PL'] - summary['Tax']
    
    return summary