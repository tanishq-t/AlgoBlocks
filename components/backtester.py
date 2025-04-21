import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.backtest import run_backtest
from utils.strategy import execute_strategy

def display_backtester():
    """
    Display the backtesting component
    """
    st.header("Backtester")
    st.write("Test your trading strategy with historical data")
    
    # Check if we have a strategy
    if 'strategy' not in st.session_state or not st.session_state.strategy.get('blocks'):
        st.warning("No strategy available. Please create a strategy in the Strategy Builder first.")
        return
    
    # Check if we have data
    if 'ticker_data' not in st.session_state or st.session_state.ticker_data is None:
        st.warning("No data available. Please load data in the Data Viewer first.")
        return
    
    # Backtest settings
    st.subheader("Backtest Settings")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        initial_capital = st.number_input("Initial Capital ($)", min_value=1000.0, max_value=10000000.0, value=100000.0, step=1000.0)
    with col2:
        commission = st.number_input("Commission (%)", min_value=0.0, max_value=5.0, value=0.1, step=0.01) / 100
    with col3:
        # Select date range for backtesting (default to all available data)
        if 'date_range' in st.session_state:
            default_start = st.session_state.date_range[0]
            default_end = st.session_state.date_range[1]
        else:
            default_start = datetime.now() - timedelta(days=365)
            default_end = datetime.now()
        
        use_full_range = st.checkbox("Use Full Data Range", value=True)
    
    if not use_full_range:
        col1, col2 = st.columns(2)
        with col1:
            backtest_start = st.date_input("Backtest Start Date", default_start)
        with col2:
            backtest_end = st.date_input("Backtest End Date", default_end)
    else:
        # Use the full data range
        backtest_start = st.session_state.ticker_data.index[0]
        backtest_end = st.session_state.ticker_data.index[-1]
    
    # Run backtest button
    if st.button("Run Backtest"):
        with st.spinner("Running backtest..."):
            # Filter data for the selected date range
            mask = (st.session_state.ticker_data.index >= pd.Timestamp(backtest_start)) & (st.session_state.ticker_data.index <= pd.Timestamp(backtest_end))
            backtest_data = st.session_state.ticker_data[mask].copy()
            
            if backtest_data.empty:
                st.error("No data available for the selected date range")
                return
            
            # Run the backtest
            backtest_results = run_backtest(
                backtest_data,
                st.session_state.strategy,
                initial_capital=initial_capital,
                commission=commission
            )
            
            # Store results in session state
            st.session_state.backtest_results = backtest_results
            
            st.success("Backtest completed successfully!")
    
    # Display backtest results if available
    if 'backtest_results' in st.session_state and st.session_state.backtest_results:
        display_backtest_results(st.session_state.backtest_results, st.session_state.ticker_data)

def display_backtest_results(results, price_data):
    """
    Display the results of a backtest
    
    Parameters:
    -----------
    results : dict
        Backtest results from run_backtest
    price_data : pd.DataFrame
        Original price data
    """
    st.markdown("---")
    st.subheader("Backtest Results")
    
    # Extract results
    equity_curve = results.get('equity_curve')
    trades = results.get('trades')
    metrics = results.get('metrics')
    final_equity = results.get('final_equity')
    
    # Handle case with no trades
    if trades is None or trades.empty:
        st.warning("No trades were executed during the backtest period.")
        return
    
    # Key metrics summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Final Equity", f"${final_equity:.2f}")
    with col2:
        st.metric("Total Return", f"{metrics.get('total_return', 0):.2f}%")
    with col3:
        st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}")
    with col4:
        st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0):.2f}%")
    
    # Equity curve chart
    st.subheader("Equity Curve")
    
    if equity_curve is not None and not equity_curve.empty:
        # Create plotly figure
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
                fig.add_trace(go.Scatter(
                    x=buy_trades['date'],
                    y=[equity_curve.loc[equity_curve['date'] == date, 'equity'].iloc[0] if date in equity_curve['date'].values else None for date in buy_trades['date']],
                    mode='markers',
                    name='Buy',
                    marker=dict(color='green', size=10, symbol='triangle-up')
                ))
            
            if not sell_trades.empty:
                fig.add_trace(go.Scatter(
                    x=sell_trades['date'],
                    y=[equity_curve.loc[equity_curve['date'] == date, 'equity'].iloc[0] if date in equity_curve['date'].values else None for date in sell_trades['date']],
                    mode='markers',
                    name='Sell',
                    marker=dict(color='red', size=10, symbol='triangle-down')
                ))
        
        # Update layout
        fig.update_layout(
            title='Equity Curve',
            xaxis_title='Date',
            yaxis_title='Equity ($)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No equity curve data available")
    
    # Trade statistics
    st.subheader("Trade Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Trades", metrics.get('total_trades', 0))
    with col2:
        st.metric("Win Rate", f"{metrics.get('win_rate', 0):.2f}%")
    with col3:
        st.metric("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}")
    
    # List of trades
    st.subheader("Trade List")
    
    if trades is not None and not trades.empty:
        # Format the dataframe for display
        display_trades = trades.copy()
        
        # Format date column
        if 'date' in display_trades.columns:
            display_trades['date'] = display_trades['date'].astype(str)
        
        # Format numeric columns
        numeric_cols = ['price', 'shares', 'value', 'commission', 'pnl', 'pnl_pct']
        for col in numeric_cols:
            if col in display_trades.columns:
                display_trades[col] = display_trades[col].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
        
        # Rename columns for display
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
        
        # Display trades table
        st.dataframe(display_trades, use_container_width=True)
    else:
        st.info("No trades were executed")
    
    # Performance metrics
    st.subheader("Performance Metrics")
    
    metrics_df = pd.DataFrame({
        'Metric': [
            'Total Return (%)',
            'Annual Return (%)',
            'Sharpe Ratio',
            'Max Drawdown (%)',
            'Total Trades',
            'Winning Trades',
            'Losing Trades',
            'Win Rate (%)',
            'Profit Factor'
        ],
        'Value': [
            f"{metrics.get('total_return', 0):.2f}",
            f"{metrics.get('annual_return', 0):.2f}",
            f"{metrics.get('sharpe_ratio', 0):.2f}",
            f"{metrics.get('max_drawdown', 0):.2f}",
            metrics.get('total_trades', 0),
            metrics.get('winning_trades', 0),
            metrics.get('losing_trades', 0),
            f"{metrics.get('win_rate', 0):.2f}",
            f"{metrics.get('profit_factor', 0):.2f}"
        ]
    })
    
    st.dataframe(metrics_df, use_container_width=True)
