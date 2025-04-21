import pandas as pd
import numpy as np

def add_moving_average(df, column='Close', period=20, ma_type='simple'):
    """
    Add moving average to dataframe
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with price data
    column : str
        Column to calculate MA on
    period : int
        Period for moving average
    ma_type : str
        Type of moving average ('simple', 'exponential', 'weighted')
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with added moving average column
    """
    result = df.copy()
    
    if ma_type == 'simple':
        result[f'SMA_{period}'] = result[column].rolling(window=period).mean()
    elif ma_type == 'exponential':
        result[f'EMA_{period}'] = result[column].ewm(span=period, adjust=False).mean()
    elif ma_type == 'weighted':
        weights = np.arange(1, period + 1)
        result[f'WMA_{period}'] = result[column].rolling(period).apply(
            lambda x: np.sum(weights * x) / weights.sum(), raw=True
        )
    
    return result

def add_rsi(df, column='Close', period=14):
    """
    Add Relative Strength Index (RSI) to dataframe
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with price data
    column : str
        Column to calculate RSI on
    period : int
        Period for RSI calculation
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with added RSI column
    """
    result = df.copy()
    
    # Calculate price changes
    delta = result[column].diff()
    
    # Create two series: gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gains and losses over the period
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate relative strength
    rs = avg_gain / avg_loss
    
    # Calculate RSI
    result[f'RSI_{period}'] = 100 - (100 / (1 + rs))
    
    return result

def add_bollinger_bands(df, column='Close', period=20, stdev=2):
    """
    Add Bollinger Bands to dataframe
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with price data
    column : str
        Column to calculate Bollinger Bands on
    period : int
        Period for Bollinger Bands calculation
    stdev : int
        Standard deviation for the bands
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with added Bollinger Bands columns
    """
    result = df.copy()
    sma = result[column].rolling(window=period).mean()
    rolling_std = result[column].rolling(window=period).std()
    
    result[f'BB_Upper_{period}'] = sma + (rolling_std * stdev)
    result[f'BB_Middle_{period}'] = sma
    result[f'BB_Lower_{period}'] = sma - (rolling_std * stdev)
    
    return result

def add_macd(df, column='Close', fast=12, slow=26, signal=9):
    """
    Add Moving Average Convergence Divergence (MACD) to dataframe
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with price data
    column : str
        Column to calculate MACD on
    fast : int
        Fast period for MACD calculation
    slow : int
        Slow period for MACD calculation
    signal : int
        Signal period for MACD calculation
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with added MACD columns
    """
    result = df.copy()
    ema_fast = result[column].ewm(span=fast, adjust=False).mean()
    ema_slow = result[column].ewm(span=slow, adjust=False).mean()
    
    result['MACD_Line'] = ema_fast - ema_slow
    result['MACD_Signal'] = result['MACD_Line'].ewm(span=signal, adjust=False).mean()
    result['MACD_Histogram'] = result['MACD_Line'] - result['MACD_Signal']
    
    return result

def add_atr(df, period=14):
    """
    Add Average True Range (ATR) to dataframe
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with price data (must have High, Low, Close columns)
    period : int
        Period for ATR calculation
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with added ATR column
    """
    result = df.copy()
    
    # Calculate True Range
    result['TR'] = pd.DataFrame({
        'HL': result['High'] - result['Low'],
        'HC': abs(result['High'] - result['Close'].shift(1)),
        'LC': abs(result['Low'] - result['Close'].shift(1))
    }).max(axis=1)
    
    # Calculate ATR
    result[f'ATR_{period}'] = result['TR'].rolling(window=period).mean()
    
    # Drop temporary column
    result.drop('TR', axis=1, inplace=True)
    
    return result

def add_stochastic_oscillator(df, k_period=14, d_period=3):
    """
    Add Stochastic Oscillator to dataframe
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with price data (must have High, Low, Close columns)
    k_period : int
        Period for %K line
    d_period : int
        Period for %D line (signal)
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with added Stochastic Oscillator columns
    """
    result = df.copy()
    
    # Calculate %K
    low_min = result['Low'].rolling(window=k_period).min()
    high_max = result['High'].rolling(window=k_period).max()
    
    result['%K'] = 100 * ((result['Close'] - low_min) / (high_max - low_min))
    
    # Calculate %D (signal line)
    result['%D'] = result['%K'].rolling(window=d_period).mean()
    
    return result

def add_all_indicators(df):
    """
    Add all available indicators to dataframe
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with price data
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with all indicators added
    """
    result = df.copy()
    
    # Add indicators
    result = add_moving_average(result, period=20, ma_type='simple')
    result = add_moving_average(result, period=50, ma_type='simple')
    result = add_moving_average(result, period=200, ma_type='simple')
    
    result = add_moving_average(result, period=20, ma_type='exponential')
    result = add_moving_average(result, period=50, ma_type='exponential')
    
    result = add_rsi(result)
    result = add_bollinger_bands(result)
    result = add_macd(result)
    result = add_atr(result)
    result = add_stochastic_oscillator(result)
    
    return result
