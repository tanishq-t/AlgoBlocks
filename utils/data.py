import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def get_stock_data(ticker, start_date, end_date):
    """
    Fetch stock data from Yahoo Finance
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    start_date : datetime or str
        Start date for data
    end_date : datetime or str
        End date for data
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with OHLCV data
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def prepare_data(df):
    """
    Prepare data for analysis and strategy execution
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw OHLCV data
        
    Returns:
    --------
    pd.DataFrame
        Prepared data with additional columns
    """
    if df.empty:
        return df
    
    # Create a copy to avoid modifying the original
    result = df.copy()
    
    # Calculate returns
    result['daily_return'] = result['Close'].pct_change() * 100
    result['cumulative_return'] = (1 + result['daily_return'] / 100).cumprod() - 1
    
    # Calculate volatility (rolling 21-day standard deviation of returns)
    result['volatility'] = result['daily_return'].rolling(window=21).std()
    
    # Calculate log returns for analysis
    result['log_return'] = np.log(result['Close'] / result['Close'].shift(1))
    
    return result

def get_available_tickers():
    """
    Get a list of popular stock tickers
    
    Returns:
    --------
    list
        List of popular stock tickers
    """
    # A list of popular stock tickers for demonstration
    return [
        'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 
        'TSLA', 'NVDA', 'JPM', 'V', 'JNJ',
        'WMT', 'PG', 'DIS', 'NFLX', 'PYPL',
        'INTC', 'AMD', 'BA', 'CSCO', 'ORCL'
    ]

def resample_data(df, timeframe='1d'):
    """
    Resample data to a different timeframe
    
    Parameters:
    -----------
    df : pd.DataFrame
        OHLCV data
    timeframe : str
        Target timeframe ('1d', '1w', '1m')
        
    Returns:
    --------
    pd.DataFrame
        Resampled data
    """
    if df.empty:
        return df
    
    # Create a copy
    result = df.copy()
    
    # Map timeframe to pandas resampling rule
    timeframe_map = {
        '1d': 'D',
        '1w': 'W',
        '1m': 'M'
    }
    
    rule = timeframe_map.get(timeframe, 'D')
    
    # Resample
    resampled = result.resample(rule).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    
    return resampled.dropna()
