import pandas as pd
import numpy as np
from datetime import datetime
from utils.strategy import execute_strategy

def run_backtest(data, strategy, initial_capital=100000.0, commission=0.001):
    """
    Run a backtest for a given strategy on historical data
    
    Parameters:
    -----------
    data : pd.DataFrame
        Historical price data
    strategy : dict
        Strategy configuration (blocks and connections)
    initial_capital : float
        Starting capital for the backtest
    commission : float
        Commission rate per trade (as a decimal)
        
    Returns:
    --------
    dict
        Backtest results including trades, equity curve, and performance metrics
    """
    # Make a copy of the data to avoid modifying the original
    df = data.copy()
    
    # Execute strategy to get buy/sell signals
    df = execute_strategy(df, strategy)
    
    # Initialize backtest variables
    position = 0  # 0 = no position, 1 = long
    capital = initial_capital
    shares = 0
    entry_price = 0
    trades = []
    equity = []
    
    # Run through the data
    for i, row in df.iterrows():
        # Record equity at each time step
        equity_value = capital
        if position == 1:
            equity_value = capital + (shares * row['Close'])
        
        equity.append({
            'date': i,
            'equity': equity_value
        })
        
        # Check for buy signal
        if row.get('signal', 0) == 1 and position == 0:
            # Calculate number of shares to buy (use all available capital)
            shares = (capital * (1 - commission)) // row['Close']
            
            # Update position and capital
            position = 1
            entry_price = row['Close']
            capital -= shares * row['Close'] * (1 + commission)
            
            # Record trade
            trades.append({
                'type': 'buy',
                'date': i,
                'price': row['Close'],
                'shares': shares,
                'value': shares * row['Close'],
                'commission': shares * row['Close'] * commission
            })
        
        # Check for sell signal
        elif (row.get('signal', 0) == -1 or row.get('exit_signal', 0) == 1) and position == 1:
            # Update capital
            capital += shares * row['Close'] * (1 - commission)
            
            # Record trade
            trade_pnl = shares * (row['Close'] - entry_price) - (shares * row['Close'] * commission) - (shares * entry_price * commission)
            trade_pnl_pct = (row['Close'] / entry_price - 1) * 100 - (commission * 2 * 100)
            
            trades.append({
                'type': 'sell',
                'date': i,
                'price': row['Close'],
                'shares': shares,
                'value': shares * row['Close'],
                'commission': shares * row['Close'] * commission,
                'pnl': trade_pnl,
                'pnl_pct': trade_pnl_pct
            })
            
            # Reset position
            position = 0
            shares = 0
            entry_price = 0
    
    # Final equity calculation
    final_equity = capital
    if position == 1:
        final_equity = capital + (shares * df['Close'].iloc[-1])
    
    # Create equity curve DataFrame
    equity_df = pd.DataFrame(equity)
    if not equity_df.empty:
        equity_df['return'] = equity_df['equity'].pct_change()
        equity_df['cumulative_return'] = (1 + equity_df['return']).cumprod() - 1
    
    # Calculate performance metrics
    metrics = calculate_performance_metrics(equity_df, trades, initial_capital)
    
    # Create trades DataFrame
    trades_df = pd.DataFrame(trades)
    
    return {
        'equity_curve': equity_df,
        'trades': trades_df,
        'metrics': metrics,
        'final_equity': final_equity
    }

def calculate_performance_metrics(equity_df, trades, initial_capital):
    """
    Calculate performance metrics from backtest results
    
    Parameters:
    -----------
    equity_df : pd.DataFrame
        Equity curve data
    trades : list
        List of trades executed
    initial_capital : float
        Initial capital used for the backtest
        
    Returns:
    --------
    dict
        Performance metrics
    """
    metrics = {}
    
    # Skip metrics calculation if no trades or empty equity curve
    if len(trades) == 0 or equity_df.empty:
        return {
            'total_return': 0,
            'annual_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
    
    # Get only sell trades to calculate win/loss metrics
    sell_trades = [t for t in trades if t['type'] == 'sell']
    
    # Basic metrics
    metrics['total_return'] = (equity_df['equity'].iloc[-1] / initial_capital - 1) * 100
    
    # Calculate trading days and annualized return
    start_date = equity_df['date'].iloc[0]
    end_date = equity_df['date'].iloc[-1]
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    trading_days = (end_date - start_date).days
    if trading_days > 0:
        annual_return = (1 + metrics['total_return']/100) ** (365 / trading_days) - 1
        metrics['annual_return'] = annual_return * 100
    else:
        metrics['annual_return'] = 0
    
    # Risk metrics
    if 'return' in equity_df.columns and not equity_df['return'].isna().all():
        daily_returns = equity_df['return'].dropna()
        if len(daily_returns) > 0:
            metrics['sharpe_ratio'] = (daily_returns.mean() / daily_returns.std()) * (252 ** 0.5) if daily_returns.std() != 0 else 0
        else:
            metrics['sharpe_ratio'] = 0
    else:
        metrics['sharpe_ratio'] = 0
    
    # Max drawdown
    if 'equity' in equity_df.columns:
        equity_series = equity_df['equity']
        rolling_max = equity_series.cummax()
        drawdown = (equity_series / rolling_max - 1) * 100
        metrics['max_drawdown'] = abs(drawdown.min())
    else:
        metrics['max_drawdown'] = 0
    
    # Trade metrics
    metrics['total_trades'] = len(sell_trades)
    metrics['winning_trades'] = sum(1 for t in sell_trades if t.get('pnl', 0) > 0)
    metrics['losing_trades'] = sum(1 for t in sell_trades if t.get('pnl', 0) <= 0)
    
    if metrics['total_trades'] > 0:
        metrics['win_rate'] = (metrics['winning_trades'] / metrics['total_trades']) * 100
    else:
        metrics['win_rate'] = 0
    
    # Profit factor
    total_profit = sum(t.get('pnl', 0) for t in sell_trades if t.get('pnl', 0) > 0)
    total_loss = sum(abs(t.get('pnl', 0)) for t in sell_trades if t.get('pnl', 0) < 0)
    
    if total_loss > 0:
        metrics['profit_factor'] = total_profit / total_loss
    else:
        metrics['profit_factor'] = 0 if total_profit == 0 else float('inf')
    
    return metrics
