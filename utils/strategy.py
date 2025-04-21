import pandas as pd
import numpy as np
from utils.indicators import (
    add_moving_average, add_rsi, add_bollinger_bands,
    add_macd, add_atr, add_stochastic_oscillator
)

def execute_strategy(data, strategy):
    """
    Execute a trading strategy defined by blocks and connections
    
    Parameters:
    -----------
    data : pd.DataFrame
        Price data with OHLCV columns
    strategy : dict
        Strategy configuration with blocks and connections
        
    Returns:
    --------
    pd.DataFrame
        Data with added signal columns
    """
    df = data.copy()
    
    # Check if strategy contains blocks
    if not strategy or 'blocks' not in strategy or not strategy['blocks']:
        df['signal'] = 0
        return df
    
    # Add indicators based on blocks
    df = add_indicators_from_blocks(df, strategy['blocks'])
    
    # Generate signals based on the strategy logic
    df = generate_signals(df, strategy)
    
    return df

def add_indicators_from_blocks(df, blocks):
    """
    Add technical indicators to the dataframe based on the blocks in the strategy
    
    Parameters:
    -----------
    df : pd.DataFrame
        Price data
    blocks : list
        List of block configurations
        
    Returns:
    --------
    pd.DataFrame
        Data with added indicators
    """
    result = df.copy()
    
    for block in blocks:
        block_type = block.get('type')
        params = block.get('params', {})
        
        if block_type == 'moving_average':
            period = params.get('period', 20)
            ma_type = params.get('ma_type', 'simple')
            result = add_moving_average(result, period=period, ma_type=ma_type)
        
        elif block_type == 'rsi':
            period = params.get('period', 14)
            result = add_rsi(result, period=period)
        
        elif block_type == 'bollinger_bands':
            period = params.get('period', 20)
            stdev = params.get('stdev', 2)
            result = add_bollinger_bands(result, period=period, stdev=stdev)
        
        elif block_type == 'macd':
            fast = params.get('fast', 12)
            slow = params.get('slow', 26)
            signal = params.get('signal', 9)
            result = add_macd(result, fast=fast, slow=slow, signal=signal)
        
        elif block_type == 'atr':
            period = params.get('period', 14)
            result = add_atr(result, period=period)
        
        elif block_type == 'stochastic':
            k_period = params.get('k_period', 14)
            d_period = params.get('d_period', 3)
            result = add_stochastic_oscillator(result, k_period=k_period, d_period=d_period)
    
    return result

def generate_signals(df, strategy):
    """
    Generate trading signals based on the strategy logic
    
    Parameters:
    -----------
    df : pd.DataFrame
        Price data with indicators
    strategy : dict
        Strategy configuration with blocks and connections
        
    Returns:
    --------
    pd.DataFrame
        Data with added signal columns
    """
    result = df.copy()
    
    # Initialize signal columns
    result['signal'] = 0  # 1 for buy, -1 for sell, 0 for hold
    result['exit_signal'] = 0  # 1 for exit
    
    blocks = strategy.get('blocks', [])
    connections = strategy.get('connections', [])
    
    # Find entry and exit condition blocks
    entry_blocks = [b for b in blocks if b.get('type') == 'entry_condition']
    exit_blocks = [b for b in blocks if b.get('type') == 'exit_condition']
    
    # Process entry conditions
    for block in entry_blocks:
        condition = block.get('params', {}).get('condition')
        if condition:
            # Parse and evaluate the condition
            signal = evaluate_condition(result, condition)
            if signal is not None:
                # Apply entry signal
                result.loc[signal, 'signal'] = 1
    
    # Process exit conditions
    for block in exit_blocks:
        condition = block.get('params', {}).get('condition')
        if condition:
            # Parse and evaluate the condition
            signal = evaluate_condition(result, condition)
            if signal is not None:
                # Apply exit signal
                result.loc[signal, 'exit_signal'] = 1
    
    # Handle risk management blocks
    stop_loss_blocks = [b for b in blocks if b.get('type') == 'stop_loss']
    take_profit_blocks = [b for b in blocks if b.get('type') == 'take_profit']
    
    # TODO: Implement stop loss and take profit logic
    # This requires tracking the entry price and calculating exit signals
    # based on price movements
    
    return result

def evaluate_condition(df, condition):
    """
    Evaluate a condition string on a dataframe
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data with indicators
    condition : str
        Condition to evaluate
        
    Returns:
    --------
    pd.Series or None
        Boolean series that can be used for indexing, or None if invalid
    """
    try:
        # Example conditions (simplified):
        # "SMA_20 > SMA_50"
        # "RSI_14 < 30"
        # "Close > BB_Upper_20"
        
        # Simple condition parser (in a real app, this would be more robust)
        if '>' in condition:
            left, right = condition.split('>')
            left = left.strip()
            right = right.strip()
            
            if left in df.columns and right in df.columns:
                return df[left] > df[right]
            elif left in df.columns:
                return df[left] > float(right)
            elif right in df.columns:
                return float(left) > df[right]
        
        elif '<' in condition:
            left, right = condition.split('<')
            left = left.strip()
            right = right.strip()
            
            if left in df.columns and right in df.columns:
                return df[left] < df[right]
            elif left in df.columns:
                return df[left] < float(right)
            elif right in df.columns:
                return float(left) < df[right]
        
        elif '==' in condition:
            left, right = condition.split('==')
            left = left.strip()
            right = right.strip()
            
            if left in df.columns and right in df.columns:
                return df[left] == df[right]
            elif left in df.columns:
                return df[left] == float(right)
            elif right in df.columns:
                return float(left) == df[right]
        
    except Exception as e:
        print(f"Error evaluating condition: {condition}, Error: {e}")
        return None
    
    return None
