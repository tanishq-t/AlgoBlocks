import pandas as pd
import numpy as np
from datetime import datetime

def calculate_equity_stats(equity_curve):
    """
    Calculate statistics from an equity curve
    
    Parameters:
    -----------
    equity_curve : pd.DataFrame
        DataFrame with equity values over time
        
    Returns:
    --------
    dict
        Statistics calculated from the equity curve
    """
    if equity_curve.empty:
        return {
            'total_return': 0,
            'annualized_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_duration': 0,
            'calmar_ratio': 0
        }
    
    # Extract equity values
    equity = equity_curve['equity']
    
    # Calculate returns
    returns = equity.pct_change().dropna()
    
    # Calculate basic statistics
    start_equity = equity.iloc[0]
    end_equity = equity.iloc[-1]
    total_return = (end_equity / start_equity - 1) * 100
    
    # Calculate trading days and annualized return
    start_date = equity_curve['date'].iloc[0]
    end_date = equity_curve['date'].iloc[-1]
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    days = (end_date - start_date).days
    if days > 0:
        years = days / 365.0
        annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100
    else:
        annualized_return = 0
    
    # Calculate volatility
    if not returns.empty:
        daily_volatility = returns.std() * 100
        annualized_volatility = daily_volatility * np.sqrt(252)
    else:
        daily_volatility = 0
        annualized_volatility = 0
    
    # Calculate Sharpe ratio (assuming risk-free rate of 0%)
    if annualized_volatility > 0:
        sharpe_ratio = annualized_return / annualized_volatility
    else:
        sharpe_ratio = 0
    
    # Calculate Sortino ratio (downside risk only)
    negative_returns = returns[returns < 0]
    if not negative_returns.empty and negative_returns.std() > 0:
        downside_deviation = negative_returns.std() * np.sqrt(252) * 100
        sortino_ratio = annualized_return / downside_deviation
    else:
        sortino_ratio = 0
    
    # Calculate maximum drawdown
    rolling_max = equity.cummax()
    drawdown = (equity / rolling_max - 1) * 100
    max_drawdown = abs(drawdown.min())
    
    # Calculate drawdown duration
    is_drawdown = equity < rolling_max
    
    # Initialize drawdown duration
    max_duration = 0
    current_duration = 0
    
    # Calculate max drawdown duration
    for is_dd in is_drawdown:
        if is_dd:
            current_duration += 1
        else:
            if current_duration > max_duration:
                max_duration = current_duration
            current_duration = 0
    
    # Check if we ended in a drawdown
    if current_duration > max_duration:
        max_duration = current_duration
    
    # Calculate Calmar ratio
    if max_drawdown > 0:
        calmar_ratio = annualized_return / max_drawdown
    else:
        calmar_ratio = 0
    
    return {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'volatility': annualized_volatility,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown,
        'max_drawdown_duration': max_duration,
        'calmar_ratio': calmar_ratio
    }

def analyze_trades(trades):
    """
    Analyze trade statistics
    
    Parameters:
    -----------
    trades : pd.DataFrame
        DataFrame with trade data
        
    Returns:
    --------
    dict
        Trade statistics
    """
    if trades.empty:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'profit_factor': 0,
            'avg_trade': 0
        }
    
    # Filter only sell trades (to count completed trades)
    sell_trades = trades[trades['type'] == 'sell']
    
    if sell_trades.empty:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'profit_factor': 0,
            'avg_trade': 0
        }
    
    # Count trades
    total_trades = len(sell_trades)
    winning_trades = len(sell_trades[sell_trades['pnl'] > 0])
    losing_trades = len(sell_trades[sell_trades['pnl'] <= 0])
    
    # Calculate win rate
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    
    # Calculate average win and loss
    winning_pnls = sell_trades[sell_trades['pnl'] > 0]['pnl']
    losing_pnls = sell_trades[sell_trades['pnl'] <= 0]['pnl']
    
    avg_win = winning_pnls.mean() if not winning_pnls.empty else 0
    avg_loss = losing_pnls.mean() if not losing_pnls.empty else 0
    
    # Calculate largest win and loss
    largest_win = winning_pnls.max() if not winning_pnls.empty else 0
    largest_loss = losing_pnls.min() if not losing_pnls.empty else 0
    
    # Calculate profit factor
    total_profit = winning_pnls.sum() if not winning_pnls.empty else 0
    total_loss = abs(losing_pnls.sum()) if not losing_pnls.empty else 0
    
    profit_factor = total_profit / total_loss if total_loss != 0 else 0
    
    # Calculate average trade
    avg_trade = sell_trades['pnl'].mean()
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'largest_win': largest_win,
        'largest_loss': largest_loss,
        'profit_factor': profit_factor,
        'avg_trade': avg_trade
    }

def calculate_monthly_returns(equity_curve):
    """
    Calculate monthly returns from an equity curve
    
    Parameters:
    -----------
    equity_curve : pd.DataFrame
        DataFrame with equity values over time
        
    Returns:
    --------
    pd.DataFrame
        Monthly returns
    """
    if equity_curve.empty:
        return pd.DataFrame()
    
    # Convert date to datetime if it's a string
    if isinstance(equity_curve['date'].iloc[0], str):
        equity_curve['date'] = pd.to_datetime(equity_curve['date'])
    
    # Set date as index for resampling
    df = equity_curve.set_index('date')
    
    # Extract equity values
    equity = df['equity']
    
    # Resample to get month-end values
    monthly_equity = equity.resample('M').last()
    
    # Calculate monthly returns
    monthly_returns = monthly_equity.pct_change() * 100
    
    # Create a DataFrame with month and year columns
    result = pd.DataFrame({
        'year': monthly_returns.index.year,
        'month': monthly_returns.index.month,
        'return': monthly_returns.values
    }).dropna()
    
    return result

def calculate_drawdowns(equity_curve):
    """
    Calculate drawdowns from an equity curve
    
    Parameters:
    -----------
    equity_curve : pd.DataFrame
        DataFrame with equity values over time
        
    Returns:
    --------
    pd.DataFrame
        Drawdowns
    """
    if equity_curve.empty:
        return pd.DataFrame()
    
    # Extract equity values
    equity = equity_curve['equity']
    
    # Calculate drawdowns
    rolling_max = equity.cummax()
    drawdown = (equity / rolling_max - 1) * 100
    
    # Create a DataFrame with drawdowns
    result = pd.DataFrame({
        'date': equity_curve['date'],
        'equity': equity,
        'peak': rolling_max,
        'drawdown': drawdown
    })
    
    return result
