import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
from utils.strategy import execute_strategy

def display_paper_trading():
    """
    Display paper trading simulation interface
    """
    st.header("Paper Trading")
    st.write("Simulate your trading strategy with real-time market data")
    
    # Check if we have a strategy
    if 'strategy' not in st.session_state or not st.session_state.strategy.get('blocks'):
        st.warning("No strategy available. Please create a strategy in the Strategy Builder first.")
        return
    
    # Paper trading settings
    st.subheader("Simulation Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        initial_capital = st.number_input("Initial Capital ($)", min_value=1000.0, max_value=10000000.0, value=100000.0, step=1000.0)
    
    with col2:
        commission = st.number_input("Commission (%)", min_value=0.0, max_value=5.0, value=0.1, step=0.01) / 100
    
    with col3:
        risk_per_trade = st.number_input("Risk Per Trade (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1) / 100
    
    # Simulation time period
    st.subheader("Simulation Period")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sim_days = st.number_input("Simulation Days", min_value=1, max_value=30, value=5, step=1)
    
    with col2:
        # Set default end date to today and start date sim_days back
        today = datetime.now()
        default_end = today
        default_start = today - timedelta(days=sim_days)
        
        use_calendar_dates = st.checkbox("Use Calendar Dates")
    
    if use_calendar_dates:
        col1, col2 = st.columns(2)
        with col1:
            sim_start_date = st.date_input("Start Date", default_start)
        with col2:
            sim_end_date = st.date_input("End Date", default_end)
    else:
        # Use the last N days
        sim_end_date = default_end
        sim_start_date = default_end - timedelta(days=sim_days)
    
    # Run simulation button
    if st.button("Run Simulation"):
        with st.spinner("Running paper trading simulation..."):
            # Fetch data for simulation
            sim_ticker = st.session_state.selected_ticker
            sim_data = yf.download(sim_ticker, start=sim_start_date, end=sim_end_date + timedelta(days=1))
            
            if sim_data.empty:
                st.error(f"No data available for {sim_ticker} in the selected date range")
                return
            
            # Run the simulation
            results = run_paper_trading_simulation(
                sim_data,
                st.session_state.strategy,
                initial_capital=initial_capital,
                commission=commission,
                risk_per_trade=risk_per_trade
            )
            
            # Store results in session state
            st.session_state.simulation_results = results
            
            st.success("Simulation completed successfully!")
    
    # Display simulation results if available
    if 'simulation_results' in st.session_state and st.session_state.simulation_results:
        display_simulation_results(st.session_state.simulation_results)

def run_paper_trading_simulation(data, strategy, initial_capital=100000.0, commission=0.001, risk_per_trade=0.01):
    """
    Run a paper trading simulation using historical data
    
    Parameters:
    -----------
    data : pd.DataFrame
        Historical price data for simulation
    strategy : dict
        Strategy configuration
    initial_capital : float
        Initial capital for simulation
    commission : float
        Commission rate per trade
    risk_per_trade : float
        Risk percentage per trade
        
    Returns:
    --------
    dict
        Simulation results
    """
    # Make a copy of the data to avoid modifying the original
    df = data.copy()
    
    # Execute strategy to get signals
    df = execute_strategy(df, strategy)
    
    # Initialize simulation variables
    capital = initial_capital
    position = 0  # 0 = no position, 1 = long
    shares = 0
    entry_price = 0
    trades = []
    equity_history = []
    
    # Run through the data day by day
    for date, row in df.iterrows():
        # Record equity at each time step
        current_equity = capital
        if position == 1:
            current_equity = capital + (shares * row['Close'])
        
        equity_history.append({
            'date': date,
            'equity': current_equity
        })
        
        # Check for buy signal
        if row.get('signal', 0) == 1 and position == 0:
            # Calculate position size based on risk
            risk_amount = current_equity * risk_per_trade
            price = row['Close']
            
            # Simple position sizing calculation (can be more sophisticated)
            shares = int((risk_amount / price) / 0.02)  # Assuming 2% max loss per trade
            
            # Ensure position doesn't exceed available capital
            max_shares = int((capital * (1 - commission)) / price)
            shares = min(shares, max_shares)
            
            if shares > 0:
                # Enter position
                position = 1
                entry_price = price
                capital -= shares * price * (1 + commission)
                
                # Record trade
                trades.append({
                    'type': 'buy',
                    'date': date,
                    'price': price,
                    'shares': shares,
                    'value': shares * price,
                    'commission': shares * price * commission
                })
        
        # Check for sell signal
        elif (row.get('signal', 0) == -1 or row.get('exit_signal', 0) == 1) and position == 1:
            # Exit position
            price = row['Close']
            capital += shares * price * (1 - commission)
            
            # Calculate P&L
            trade_pnl = shares * (price - entry_price) - (shares * price * commission) - (shares * entry_price * commission)
            trade_pnl_pct = (price / entry_price - 1) * 100 - (commission * 2 * 100)
            
            # Record trade
            trades.append({
                'type': 'sell',
                'date': date,
                'price': price,
                'shares': shares,
                'value': shares * price,
                'commission': shares * price * commission,
                'pnl': trade_pnl,
                'pnl_pct': trade_pnl_pct
            })
            
            # Reset position
            position = 0
            shares = 0
            entry_price = 0
    
    # Calculate final equity
    final_equity = capital
    if position == 1:
        final_equity = capital + (shares * df['Close'].iloc[-1])
    
    # Create equity curve DataFrame
    equity_df = pd.DataFrame(equity_history)
    if not equity_df.empty:
        equity_df['return'] = equity_df['equity'].pct_change()
    
    # Create trades DataFrame
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    
    # Calculate performance metrics
    metrics = {}
    
    if not equity_df.empty:
        # Basic metrics
        start_equity = equity_df['equity'].iloc[0]
        end_equity = equity_df['equity'].iloc[-1]
        
        metrics['total_return'] = (end_equity / start_equity - 1) * 100
        metrics['total_trades'] = len([t for t in trades if t['type'] == 'sell'])
        
        # Win/loss metrics
        if trades:
            sell_trades = [t for t in trades if t['type'] == 'sell']
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
                metrics['profit_factor'] = float('inf') if total_profit > 0 else 0
        else:
            metrics['winning_trades'] = 0
            metrics['losing_trades'] = 0
            metrics['win_rate'] = 0
            metrics['profit_factor'] = 0
    
    return {
        'equity_curve': equity_df,
        'trades': trades_df,
        'metrics': metrics,
        'final_equity': final_equity,
        'has_open_position': position == 1,
        'open_position': {
            'shares': shares,
            'entry_price': entry_price
        } if position == 1 else None
    }

def display_simulation_results(results):
    """
    Display paper trading simulation results
    
    Parameters:
    -----------
    results : dict
        Simulation results
    """
    st.markdown("---")
    st.subheader("Simulation Results")
    
    # Extract results
    equity_curve = results.get('equity_curve')
    trades = results.get('trades')
    metrics = results.get('metrics')
    final_equity = results.get('final_equity')
    has_open_position = results.get('has_open_position', False)
    open_position = results.get('open_position')
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Final Equity", f"${final_equity:.2f}")
    with col2:
        st.metric("Total Return", f"{metrics.get('total_return', 0):.2f}%")
    with col3:
        st.metric("Total Trades", metrics.get('total_trades', 0))
    with col4:
        st.metric("Win Rate", f"{metrics.get('win_rate', 0):.2f}%")
    
    # Display open position if any
    if has_open_position and open_position:
        st.subheader("Open Position")
        
        position_df = pd.DataFrame({
            'Shares': [open_position['shares']],
            'Entry Price': [f"${open_position['entry_price']:.2f}"],
            'Current Value': [f"${open_position['shares'] * equity_curve['equity'].iloc[-1]:.2f}"]
        })
        
        st.dataframe(position_df, use_container_width=True)
    
    # Equity curve
    st.subheader("Equity Curve")
    
    if equity_curve is not None and not equity_curve.empty:
        fig = go.Figure()
        
        # Add equity curve
        fig.add_trace(go.Scatter(
            x=equity_curve['date'],
            y=equity_curve['equity'],
            mode='lines',
            name='Equity',
            line=dict(color='blue', width=2)
        ))
        
        # Add buy and sell markers
        if trades is not None and not trades.empty:
            buy_trades = trades[trades['type'] == 'buy']
            sell_trades = trades[trades['type'] == 'sell']
            
            if not buy_trades.empty:
                buy_equity = []
                for date in buy_trades['date']:
                    equity_at_date = equity_curve[equity_curve['date'] == date]['equity'].iloc[0] if date in equity_curve['date'].values else None
                    buy_equity.append(equity_at_date)
                
                fig.add_trace(go.Scatter(
                    x=buy_trades['date'],
                    y=buy_equity,
                    mode='markers',
                    name='Buy',
                    marker=dict(color='green', size=10, symbol='triangle-up')
                ))
            
            if not sell_trades.empty:
                sell_equity = []
                for date in sell_trades['date']:
                    equity_at_date = equity_curve[equity_curve['date'] == date]['equity'].iloc[0] if date in equity_curve['date'].values else None
                    sell_equity.append(equity_at_date)
                
                fig.add_trace(go.Scatter(
                    x=sell_trades['date'],
                    y=sell_equity,
                    mode='markers',
                    name='Sell',
                    marker=dict(color='red', size=10, symbol='triangle-down')
                ))
        
        # Update layout
        fig.update_layout(
            title='Paper Trading Equity Curve',
            xaxis_title='Date',
            yaxis_title='Equity ($)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Trade list
    st.subheader("Trade List")
    
    if trades is not None and not trades.empty:
        # Format trades for display
        display_trades = trades.copy()
        
        # Format date
        display_trades['date'] = display_trades['date'].astype(str)
        
        # Format numeric columns
        for col in ['price', 'shares', 'value', 'commission', 'pnl', 'pnl_pct']:
            if col in display_trades.columns:
                display_trades[col] = display_trades[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
        
        # Rename columns
        display_trades = display_trades.rename(columns={
            'type': 'Type',
            'date': 'Date',
            'price': 'Price',
            'shares': 'Shares',
            'value': 'Value',
            'commission': 'Commission',
            'pnl': 'P&L',
            'pnl_pct': 'P&L %'
        })
        
        st.dataframe(display_trades, use_container_width=True)
    else:
        st.info("No trades were executed during the simulation")
    
    # Performance metrics
    if metrics:
        st.subheader("Performance Metrics")
        
        metrics_df = pd.DataFrame({
            'Metric': [
                'Total Return (%)',
                'Total Trades',
                'Winning Trades',
                'Losing Trades',
                'Win Rate (%)',
                'Profit Factor'
            ],
            'Value': [
                f"{metrics.get('total_return', 0):.2f}",
                metrics.get('total_trades', 0),
                metrics.get('winning_trades', 0),
                metrics.get('losing_trades', 0),
                f"{metrics.get('win_rate', 0):.2f}",
                f"{metrics.get('profit_factor', 0):.2f}"
            ]
        })
        
        st.dataframe(metrics_df, use_container_width=True)
