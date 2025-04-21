import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.performance import (
    calculate_equity_stats, analyze_trades, 
    calculate_monthly_returns, calculate_drawdowns
)

def display_performance_dashboard():
    """
    Display comprehensive performance analytics for trading strategies
    """
    st.header("Performance Analytics")
    st.write("Analyze and visualize the performance of your trading strategy")
    
    # Check if backtest results are available
    if 'backtest_results' not in st.session_state or not st.session_state.backtest_results:
        st.warning("No backtest results available. Please run a backtest first.")
        return
    
    # Get results from session state
    results = st.session_state.backtest_results
    equity_curve = results.get('equity_curve')
    trades = results.get('trades')
    
    # Check if we have valid results
    if equity_curve is None or equity_curve.empty or trades is None or trades.empty:
        st.warning("Insufficient data for performance analysis. The backtest may not have produced any trades.")
        return
    
    # Calculate additional performance metrics
    equity_stats = calculate_equity_stats(equity_curve)
    trade_stats = analyze_trades(trades)
    monthly_returns = calculate_monthly_returns(equity_curve)
    drawdowns = calculate_drawdowns(equity_curve)
    
    # Performance overview dashboard
    st.subheader("Performance Overview")
    
    # Key metrics in expanded columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Return", f"{equity_stats['total_return']:.2f}%")
    with col2:
        st.metric("Annual Return", f"{equity_stats['annualized_return']:.2f}%")
    with col3:
        st.metric("Sharpe Ratio", f"{equity_stats['sharpe_ratio']:.2f}")
    with col4:
        st.metric("Max Drawdown", f"{equity_stats['max_drawdown']:.2f}%")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Win Rate", f"{trade_stats['win_rate']:.2f}%")
    with col2:
        st.metric("Profit Factor", f"{trade_stats['profit_factor']:.2f}")
    with col3:
        st.metric("Total Trades", trade_stats['total_trades'])
    with col4:
        st.metric("Avg. Trade", f"${trade_stats['avg_trade']:.2f}")
    
    # Equity curve with drawdowns
    st.subheader("Equity Curve with Drawdowns")
    
    # Create subplot with two y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add equity curve
    fig.add_trace(
        go.Scatter(x=equity_curve['date'], y=equity_curve['equity'], name="Equity", line=dict(color="blue", width=2)),
        secondary_y=False
    )
    
    # Add drawdown
    if not drawdowns.empty:
        fig.add_trace(
            go.Scatter(x=drawdowns['date'], y=drawdowns['drawdown'], name="Drawdown", line=dict(color="red", width=1)),
            secondary_y=True
        )
    
    # Update layout
    fig.update_layout(
        title_text="Equity Curve and Drawdowns",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Update axes titles
    fig.update_yaxes(title_text="Equity ($)", secondary_y=False)
    fig.update_yaxes(title_text="Drawdown (%)", secondary_y=True)
    fig.update_xaxes(title_text="Date")
    
    # Reverse the y-axis for drawdowns (negative values at the top)
    fig.update_yaxes(autorange="reversed", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Return analysis
    st.subheader("Return Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Monthly Returns", "Return Distribution", "Drawdown Analysis"])
    
    with tab1:
        # Monthly returns heatmap
        if not monthly_returns.empty:
            # Pivot the data for the heatmap
            if len(monthly_returns) > 1:
                pivot_returns = monthly_returns.pivot_table(
                    index="month", 
                    columns="year", 
                    values="return",
                    aggfunc='sum'
                ).fillna(0)
                
                # Create month labels
                month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                pivot_returns.index = [month_labels[i-1] for i in pivot_returns.index]
                
                # Create heatmap
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_returns.values,
                    x=pivot_returns.columns,
                    y=pivot_returns.index,
                    colorscale=[
                        [0, 'rgb(255,0,0)'],
                        [0.5, 'rgb(255,255,255)'],
                        [1, 'rgb(0,128,0)']
                    ],
                    colorbar=dict(title="Return (%)"),
                    text=[[f"{val:.2f}%" for val in row] for row in pivot_returns.values],
                    hoverinfo="text",
                    zmid=0
                ))
                
                fig.update_layout(
                    title="Monthly Returns (%)",
                    xaxis_title="Year",
                    yaxis_title="Month",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data for monthly returns heatmap")
        else:
            st.info("No monthly returns data available")
    
    with tab2:
        # Return distribution
        if 'return' in equity_curve.columns:
            returns = equity_curve['return'].dropna() * 100  # Convert to percentage
            
            # Create histogram
            fig = px.histogram(
                returns, 
                nbins=50,
                title="Daily Returns Distribution",
                labels={"value": "Return (%)"},
                color_discrete_sequence=['blue']
            )
            
            # Add normal distribution curve
            mean = returns.mean()
            std = returns.std()
            x = np.linspace(min(returns), max(returns), 100)
            y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2) * len(returns) * (returns.max() - returns.min()) / 50
            
            fig.add_trace(
                go.Scatter(
                    x=x, 
                    y=y, 
                    mode='lines', 
                    name='Normal Distribution',
                    line=dict(color='red', width=2)
                )
            )
            
            fig.update_layout(
                xaxis_title="Return (%)",
                yaxis_title="Frequency",
                template="plotly_white",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean Return", f"{mean:.2f}%")
            with col2:
                st.metric("Std Dev", f"{std:.2f}%")
            with col3:
                st.metric("Skewness", f"{returns.skew():.2f}")
            with col4:
                st.metric("Kurtosis", f"{returns.kurtosis():.2f}")
        else:
            st.info("No return data available")
    
    with tab3:
        # Drawdown analysis
        if not drawdowns.empty:
            # Find significant drawdowns (e.g., more than 5%)
            significant_dd = drawdowns[drawdowns['drawdown'] <= -5]
            
            if not significant_dd.empty:
                # Group into drawdown periods
                dd_periods = []
                current_dd = []
                
                for i, row in significant_dd.iterrows():
                    if not current_dd or (i > 0 and row['date'] == significant_dd.iloc[current_dd[-1]]['date'] + pd.Timedelta(days=1)):
                        current_dd.append(i)
                    else:
                        # New drawdown period
                        if current_dd:
                            dd_periods.append(current_dd)
                        current_dd = [i]
                
                # Add the last drawdown period
                if current_dd:
                    dd_periods.append(current_dd)
                
                # Calculate drawdown stats
                dd_stats = []
                for period in dd_periods:
                    dd_data = significant_dd.iloc[period]
                    max_dd = dd_data['drawdown'].min()
                    start_date = dd_data.iloc[0]['date']
                    end_date = dd_data.iloc[-1]['date']
                    duration = (end_date - start_date).days
                    
                    dd_stats.append({
                        'Start Date': start_date,
                        'End Date': end_date,
                        'Duration (days)': duration,
                        'Max Drawdown (%)': max_dd
                    })
                
                # Convert to DataFrame
                dd_df = pd.DataFrame(dd_stats)
                
                # Show table
                st.write("Major Drawdown Periods")
                st.dataframe(dd_df, use_container_width=True)
                
                # Plot top drawdowns
                fig = go.Figure()
                
                for i, dd in enumerate(dd_stats[:5]):  # Show top 5 drawdowns
                    dd_period = drawdowns[(drawdowns['date'] >= dd['Start Date']) & (drawdowns['date'] <= dd['End Date'])]
                    
                    fig.add_trace(go.Scatter(
                        x=dd_period['date'],
                        y=dd_period['drawdown'],
                        mode='lines',
                        name=f"DD {i+1}: {dd['Max Drawdown (%)']:.2f}%"
                    ))
                
                fig.update_layout(
                    title="Top 5 Drawdown Periods",
                    xaxis_title="Date",
                    yaxis_title="Drawdown (%)",
                    template="plotly_white",
                    yaxis=dict(autorange="reversed")  # Negative values at top
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No significant drawdowns detected")
            
            # Drawdown duration histogram
            if not drawdowns.empty:
                # Calculate drawdown durations
                in_drawdown = False
                current_duration = 0
                durations = []
                
                for i, row in drawdowns.iterrows():
                    if row['drawdown'] < 0:
                        if not in_drawdown:
                            in_drawdown = True
                            current_duration = 1
                        else:
                            current_duration += 1
                    else:
                        if in_drawdown:
                            durations.append(current_duration)
                            in_drawdown = False
                            current_duration = 0
                
                # Add final drawdown if still in one
                if in_drawdown:
                    durations.append(current_duration)
                
                if durations:
                    # Create histogram
                    fig = px.histogram(
                        durations, 
                        nbins=20,
                        title="Drawdown Duration Distribution",
                        labels={"value": "Duration (days)"},
                        color_discrete_sequence=['red']
                    )
                    
                    fig.update_layout(
                        xaxis_title="Duration (days)",
                        yaxis_title="Frequency",
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No drawdown durations to analyze")
        else:
            st.info("No drawdown data available")
    
    # Trade analysis
    st.subheader("Trade Analysis")
    
    tab1, tab2 = st.tabs(["Trade Statistics", "Trade Distribution"])
    
    with tab1:
        # Trade statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Win/Loss Metrics**")
            metrics = [
                {"name": "Total Trades", "value": trade_stats['total_trades']},
                {"name": "Winning Trades", "value": trade_stats['winning_trades']},
                {"name": "Losing Trades", "value": trade_stats['losing_trades']},
                {"name": "Win Rate", "value": f"{trade_stats['win_rate']:.2f}%"},
                {"name": "Profit Factor", "value": f"{trade_stats['profit_factor']:.2f}"}
            ]
            
            metrics_df = pd.DataFrame(metrics)
            st.dataframe(metrics_df, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("**Profit/Loss Metrics**")
            pnl_metrics = [
                {"name": "Average Win", "value": f"${trade_stats['avg_win']:.2f}"},
                {"name": "Average Loss", "value": f"${trade_stats['avg_loss']:.2f}"},
                {"name": "Largest Win", "value": f"${trade_stats['largest_win']:.2f}"},
                {"name": "Largest Loss", "value": f"${trade_stats['largest_loss']:.2f}"},
                {"name": "Average Trade", "value": f"${trade_stats['avg_trade']:.2f}"}
            ]
            
            pnl_df = pd.DataFrame(pnl_metrics)
            st.dataframe(pnl_df, hide_index=True, use_container_width=True)
        
        # Trade list
        st.markdown("**Recent Trades**")
        if not trades.empty:
            # Display the 10 most recent trades
            recent_trades = trades.tail(10).copy()
            
            # Format columns
            if 'date' in recent_trades.columns:
                recent_trades['date'] = recent_trades['date'].astype(str)
            
            for col in ['price', 'shares', 'value', 'commission', 'pnl', 'pnl_pct']:
                if col in recent_trades.columns:
                    recent_trades[col] = recent_trades[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
            
            # Rename columns
            recent_trades = recent_trades.rename(columns={
                'type': 'Type',
                'date': 'Date',
                'price': 'Price',
                'shares': 'Shares',
                'value': 'Value',
                'commission': 'Commission',
                'pnl': 'P&L',
                'pnl_pct': 'P&L %'
            })
            
            st.dataframe(recent_trades, use_container_width=True)
        else:
            st.info("No trades available")
    
    with tab2:
        # Trade distribution analysis
        if not trades.empty:
            # Filter to only sell trades (which have P&L)
            sell_trades = trades[trades['type'] == 'sell'].copy()
            
            if not sell_trades.empty:
                # Convert date to datetime if it's a string
                if isinstance(sell_trades['date'].iloc[0], str):
                    sell_trades['date'] = pd.to_datetime(sell_trades['date'])
                
                # Add day of week
                sell_trades['day_of_week'] = sell_trades['date'].dt.day_name()
                
                # Trade P&L distribution
                fig = px.histogram(
                    sell_trades, 
                    x="pnl",
                    nbins=30,
                    title="Trade P&L Distribution",
                    color_discrete_sequence=['green']
                )
                
                fig.update_layout(
                    xaxis_title="P&L ($)",
                    yaxis_title="Number of Trades",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Trade P&L by day of week
                fig = px.box(
                    sell_trades,
                    x="day_of_week",
                    y="pnl",
                    title="P&L by Day of Week",
                    color_discrete_sequence=['blue'],
                    category_orders={"day_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
                )
                
                fig.update_layout(
                    xaxis_title="Day of Week",
                    yaxis_title="P&L ($)",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Trade P&L over time
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=sell_trades['date'],
                    y=sell_trades['pnl'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=sell_trades['pnl'],
                        colorscale='RdYlGn',
                        cmin=sell_trades['pnl'].min(),
                        cmax=sell_trades['pnl'].max(),
                        colorbar=dict(title="P&L ($)")
                    ),
                    name="Trade P&L"
                ))
                
                fig.update_layout(
                    title="Trade P&L Over Time",
                    xaxis_title="Date",
                    yaxis_title="P&L ($)",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sell trades available for P&L analysis")
        else:
            st.info("No trades available for distribution analysis")
