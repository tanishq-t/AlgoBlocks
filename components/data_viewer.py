import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
from utils.data import get_stock_data, prepare_data, get_available_tickers, resample_data
from utils.indicators import add_all_indicators

def display_data_viewer():
    """
    Display market data viewer with interactive charts and technical indicators
    """
    st.header("Data Viewer")
    st.write("Explore market data and technical indicators")
    
    # Sidebar inputs (already handled in main app.py)
    ticker = st.session_state.selected_ticker
    start_date = st.session_state.date_range[0]
    end_date = st.session_state.date_range[1]
    
    # Check if we have data
    if 'ticker_data' not in st.session_state or st.session_state.ticker_data is None:
        st.warning(f"No data available for {ticker}. Please check the ticker symbol and date range.")
        
        # Show popular tickers for convenience
        st.subheader("Popular Tickers")
        popular_tickers = get_available_tickers()
        
        # Display in 4 columns
        cols = st.columns(4)
        for i, pop_ticker in enumerate(popular_tickers):
            col_index = i % 4
            if cols[col_index].button(pop_ticker, key=f"pop_{pop_ticker}"):
                # Update session state and trigger data fetch
                st.session_state.selected_ticker = pop_ticker
                st.rerun()
        
        return
    
    # Data controls
    st.subheader("Data Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Timeframe selection
        timeframe = st.selectbox(
            "Timeframe",
            options=["1d", "1w", "1m"],
            index=0,
            key="data_timeframe"
        )
    
    with col2:
        # Show indicators toggle
        show_indicators = st.checkbox("Show Technical Indicators", value=True)
    
    with col3:
        # Indicator count selection
        if show_indicators:
            indicator_count = st.slider(
                "Number of Indicators",
                min_value=1,
                max_value=5,
                value=3
            )
        else:
            indicator_count = 0
    
    # Get and preprocess data
    data = st.session_state.ticker_data
    
    # Resample data if needed
    if timeframe != "1d":
        data = resample_data(data, timeframe=timeframe)
    
    # Prepare data with additional columns
    data = prepare_data(data)
    
    # Display price chart
    st.subheader(f"{ticker} Price Chart")
    
    # Add indicators if requested
    if show_indicators:
        data = add_all_indicators(data)
    
    # Plot chart
    fig = create_price_chart(data, ticker, indicator_count, show_indicators)
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table with key statistics
    st.subheader("Market Data")
    
    # Data table tabs
    tab1, tab2, tab3 = st.tabs(["Price Data", "Technical Indicators", "Statistics"])
    
    with tab1:
        # Show price data table
        if not data.empty:
            # Format the data for display
            price_data = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            price_data.index = price_data.index.strftime('%Y-%m-%d')
            
            # Display the most recent data first
            st.dataframe(price_data.iloc[::-1], use_container_width=True)
        else:
            st.info("No price data available")
    
    with tab2:
        # Show technical indicators
        if show_indicators and not data.empty:
            # Get indicator columns
            indicator_cols = [col for col in data.columns if any(ind in col for ind in ['SMA', 'EMA', 'RSI', 'BB_', 'MACD', '%K', '%D', 'ATR'])]
            
            if indicator_cols:
                # Create a dataframe with only indicator columns
                indicator_data = data[indicator_cols].copy()
                indicator_data.index = indicator_data.index.strftime('%Y-%m-%d')
                
                # Display the most recent data first
                st.dataframe(indicator_data.iloc[::-1], use_container_width=True)
            else:
                st.info("No indicator data available")
        else:
            st.info("Enable technical indicators to view this data")
    
    with tab3:
        # Show key statistics
        if not data.empty:
            # Get the most recent data point
            latest_data = data.iloc[-1]
            
            # Calculate key statistics
            stats = calculate_market_statistics(data, ticker)
            
            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Price Statistics")
                price_stats = pd.DataFrame({
                    'Metric': [
                        'Current Price',
                        'Day Change',
                        'Day Range',
                        'Week Change',
                        'Month Change',
                        'Volume',
                        '52-Week High',
                        '52-Week Low'
                    ],
                    'Value': [
                        f"${stats['current_price']:.2f}",
                        f"{stats['day_change']:.2f}%",
                        f"${stats['day_low']:.2f} - ${stats['day_high']:.2f}",
                        f"{stats['week_change']:.2f}%",
                        f"{stats['month_change']:.2f}%",
                        f"{stats['volume']:,.0f}",
                        f"${stats['year_high']:.2f}",
                        f"${stats['year_low']:.2f}"
                    ]
                })
                
                st.dataframe(price_stats, hide_index=True, use_container_width=True)
            
            with col2:
                st.subheader("Technical Statistics")
                if show_indicators:
                    technical_stats = pd.DataFrame({
                        'Metric': [
                            'RSI (14)',
                            'SMA (20)',
                            'SMA (50)',
                            'SMA (200)',
                            'EMA (20)',
                            'Bollinger Upper',
                            'Bollinger Lower',
                            'MACD Line'
                        ],
                        'Value': [
                            f"{data['RSI_14'].iloc[-1]:.2f}" if 'RSI_14' in data else 'N/A',
                            f"${data['SMA_20'].iloc[-1]:.2f}" if 'SMA_20' in data else 'N/A',
                            f"${data['SMA_50'].iloc[-1]:.2f}" if 'SMA_50' in data else 'N/A',
                            f"${data['SMA_200'].iloc[-1]:.2f}" if 'SMA_200' in data else 'N/A',
                            f"${data['EMA_20'].iloc[-1]:.2f}" if 'EMA_20' in data else 'N/A',
                            f"${data['BB_Upper_20'].iloc[-1]:.2f}" if 'BB_Upper_20' in data else 'N/A',
                            f"${data['BB_Lower_20'].iloc[-1]:.2f}" if 'BB_Lower_20' in data else 'N/A',
                            f"{data['MACD_Line'].iloc[-1]:.2f}" if 'MACD_Line' in data else 'N/A'
                        ]
                    })
                    
                    st.dataframe(technical_stats, hide_index=True, use_container_width=True)
                else:
                    st.info("Enable technical indicators to view statistics")
        else:
            st.info("No data available for statistics")
    
    # Download data button
    st.markdown("---")
    if not data.empty:
        download_data = data.copy()
        
        # Format index for download
        download_data.index = download_data.index.strftime('%Y-%m-%d')
        
        # Create download button
        csv = download_data.to_csv()
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"{ticker}_data.csv",
            mime="text/csv"
        )

def create_price_chart(data, ticker, indicator_count=3, show_indicators=True):
    """
    Create an interactive price chart with indicators
    
    Parameters:
    -----------
    data : pd.DataFrame
        Price data with indicators
    ticker : str
        Ticker symbol
    indicator_count : int
        Number of indicators to display
    show_indicators : bool
        Whether to show indicators
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive chart
    """
    if data.empty:
        # Return empty figure if no data
        return go.Figure()
    
    # Determine the number of rows for subplots based on indicator count
    num_rows = 1 + min(indicator_count, 3) if show_indicators else 1
    
    # Create subplot heights
    row_heights = [0.6]  # Main price chart takes 60% of height
    
    if num_rows > 1:
        for _ in range(num_rows - 1):
            row_heights.append((1 - 0.6) / (num_rows - 1))  # Divide remaining space
    
    # Create subplots
    fig = make_subplots(
        rows=num_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=get_subplot_titles(indicator_count, show_indicators)
    )
    
    # Add price candlestick chart to the first row
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=ticker
        ),
        row=1, col=1
    )
    
    # Add volume as bar chart on the same row but with secondary y-axis
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume',
            marker=dict(color='rgba(100, 100, 250, 0.3)'),
            opacity=0.3
        ),
        row=1, col=1
    )
    
    # Add indicators
    if show_indicators:
        current_row = 2  # Start from the second row for indicators
        
        # Add Moving Averages to the price chart
        if 'SMA_20' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['SMA_20'],
                    name='SMA 20',
                    line=dict(color='blue', width=1)
                ),
                row=1, col=1
            )
        
        if 'SMA_50' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['SMA_50'],
                    name='SMA 50',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
        
        if 'EMA_20' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['EMA_20'],
                    name='EMA 20',
                    line=dict(color='green', width=1)
                ),
                row=1, col=1
            )
        
        # Add Bollinger Bands to the price chart
        if all(col in data.columns for col in ['BB_Upper_20', 'BB_Middle_20', 'BB_Lower_20']):
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['BB_Upper_20'],
                    name='BB Upper',
                    line=dict(color='rgba(250, 0, 0, 0.5)', width=1, dash='dash')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['BB_Lower_20'],
                    name='BB Lower',
                    line=dict(color='rgba(250, 0, 0, 0.5)', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(250, 0, 0, 0.05)'
                ),
                row=1, col=1
            )
        
        # Add RSI indicator
        if 'RSI_14' in data.columns and current_row <= num_rows:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['RSI_14'],
                    name='RSI (14)',
                    line=dict(color='purple', width=1)
                ),
                row=current_row, col=1
            )
            
            # Add horizontal lines at 30 and 70
            fig.add_shape(
                type="line",
                x0=data.index[0],
                x1=data.index[-1],
                y0=30,
                y1=30,
                line=dict(color="red", width=1, dash="dash"),
                row=current_row, col=1
            )
            
            fig.add_shape(
                type="line",
                x0=data.index[0],
                x1=data.index[-1],
                y0=70,
                y1=70,
                line=dict(color="red", width=1, dash="dash"),
                row=current_row, col=1
            )
            
            current_row += 1
        
        # Add MACD indicator
        if all(col in data.columns for col in ['MACD_Line', 'MACD_Signal', 'MACD_Histogram']) and current_row <= num_rows:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['MACD_Line'],
                    name='MACD Line',
                    line=dict(color='blue', width=1)
                ),
                row=current_row, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['MACD_Signal'],
                    name='Signal Line',
                    line=dict(color='red', width=1)
                ),
                row=current_row, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['MACD_Histogram'],
                    name='Histogram',
                    marker=dict(
                        color=[
                            'green' if val >= 0 else 'red' 
                            for val in data['MACD_Histogram']
                        ]
                    )
                ),
                row=current_row, col=1
            )
            
            current_row += 1
        
        # Add Stochastic Oscillator
        if all(col in data.columns for col in ['%K', '%D']) and current_row <= num_rows:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['%K'],
                    name='%K',
                    line=dict(color='blue', width=1)
                ),
                row=current_row, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['%D'],
                    name='%D',
                    line=dict(color='red', width=1)
                ),
                row=current_row, col=1
            )
            
            # Add horizontal lines at 20 and 80
            fig.add_shape(
                type="line",
                x0=data.index[0],
                x1=data.index[-1],
                y0=20,
                y1=20,
                line=dict(color="red", width=1, dash="dash"),
                row=current_row, col=1
            )
            
            fig.add_shape(
                type="line",
                x0=data.index[0],
                x1=data.index[-1],
                y0=80,
                y1=80,
                line=dict(color="red", width=1, dash="dash"),
                row=current_row, col=1
            )
    
    # Update layout
    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode="x unified",
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_rangeslider_visible=False,
        height=800 if num_rows > 1 else 500
    )
    
    # Adjust y-axis labels for each row
    for i in range(1, num_rows + 1):
        fig.update_yaxes(title_text="Price ($)" if i == 1 else "", row=i, col=1)
    
    return fig

def get_subplot_titles(indicator_count, show_indicators):
    """
    Get subplot titles based on the number of indicators
    
    Parameters:
    -----------
    indicator_count : int
        Number of indicators
    show_indicators : bool
        Whether to show indicators
        
    Returns:
    --------
    list
        List of subplot titles
    """
    titles = ["Price Chart"]
    
    if not show_indicators:
        return titles
    
    # Add indicator titles based on count and fixed order
    indicator_titles = ["RSI", "MACD", "Stochastic"]
    
    for i in range(min(indicator_count, len(indicator_titles))):
        titles.append(indicator_titles[i])
    
    return titles

def calculate_market_statistics(data, ticker):
    """
    Calculate key market statistics from price data
    
    Parameters:
    -----------
    data : pd.DataFrame
        Price data
    ticker : str
        Ticker symbol
        
    Returns:
    --------
    dict
        Dictionary of market statistics
    """
    if data.empty:
        return {}
    
    # Current values
    current_price = data['Close'].iloc[-1]
    previous_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
    
    # Day range
    day_high = data['High'].iloc[-1]
    day_low = data['Low'].iloc[-1]
    
    # Calculate changes
    day_change_pct = ((current_price / previous_close) - 1) * 100
    
    # Week change (5 trading days)
    week_lookback = min(5, len(data) - 1)
    week_price = data['Close'].iloc[-week_lookback-1] if week_lookback > 0 else current_price
    week_change_pct = ((current_price / week_price) - 1) * 100
    
    # Month change (21 trading days)
    month_lookback = min(21, len(data) - 1)
    month_price = data['Close'].iloc[-month_lookback-1] if month_lookback > 0 else current_price
    month_change_pct = ((current_price / month_price) - 1) * 100
    
    # Year high/low (252 trading days)
    year_lookback = min(252, len(data))
    year_data = data.iloc[-year_lookback:]
    year_high = year_data['High'].max()
    year_low = year_data['Low'].min()
    
    # Volume
    volume = data['Volume'].iloc[-1]
    
    return {
        'current_price': current_price,
        'day_change': day_change_pct,
        'day_high': day_high,
        'day_low': day_low,
        'week_change': week_change_pct,
        'month_change': month_change_pct,
        'year_high': year_high,
        'year_low': year_low,
        'volume': volume
    }
