import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
import time

# Set page configuration
st.set_page_config(
    page_title="AlgoBlocks - Algorithmic Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"  # Default theme


with st.sidebar:
    theme_container = st.container()



# Apply custom CSS for styling
st.markdown("""
<style>
    /* ==============================
   AlgoBlocks - Refined UI Styling
   ============================== */

    /* Root Layout Enhancements */
    .main .block-container {
        padding: 2rem 2rem;
        max-width: 1200px;
        margin: auto;
    }

    /* Heading Glow & Font Hierarchy */
    h1 {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }

    h3 {
        color: #475569;
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 0;
        opacity: 0.9;
    }

    /* Card/Block UI: Neumorphism style */
    .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        transition: all 0.25s ease-in-out;
    }

    .block-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.08);
    }

    .block-title {
        font-weight: 600;
        font-size: 1.2rem;
        color: #1e3a8a;
    }

    .block-description {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.6;
    }

    /* Strategy Type Indicators */
    .block-indicator, .block-order, .block-risk, .block-logic {
        border-radius: 10px;
        padding: 12px;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    .block-indicator {
        background: #eff6ff;
        border-left: 5px solid #3b82f6;
    }

    .block-order {
        background: #fff7ed;
        border-left: 5px solid #f97316;
    }

    .block-risk {
        background: #fef2f2;
        border-left: 5px solid #ef4444;
    }

    .block-logic {
        background: #ecfdf5;
        border-left: 5px solid #10b981;
    }

    /* Performance Metrics */
    .performance-metric {
        border-bottom: 1px solid #e2e8f0;
        padding: 12px 0;
        display: flex;
        justify-content: space-between;
        font-weight: 500;
    }

    /* Gain/Loss Styling */
    .backtest-result-positive, .backtest-result-negative {
        display: inline-flex;
        align-items: center;
        font-weight: 600;
    }

    .backtest-result-positive {
        color: #22c55e;
    }
    .backtest-result-positive::before {
        content: "▲";
        margin-right: 6px;
    }

    .backtest-result-negative {
        color: #ef4444;
    }
    .backtest-result-negative::before {
        content: "▼";
        margin-right: 6px;
    }

    /* Input & Buttons */
    input[type="text"], div[data-baseweb="select"], textarea {
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.95rem;
        background-color: #f9fafb;
        transition: 0.2s ease;
    }

    input[type="text"]:focus {
        outline: none;
        border-color: #3b82f6;
        background-color: #fff;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }

    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1e40af);
        color: white;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
        transition: all 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, #1e40af, #2563eb);
    }

    /* Sidebar polish */
    .sidebar .sidebar-content {
        background-color: #f8fafc;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        background-color: #e0f2fe;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        margin-right: 6px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1e40af;
        font-size: 1rem;
        padding: 10px;
        background-color: #f1f5f9;
        border-radius: 6px;
    }

    /* Alerts & Notifications */
    .stAlert {
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    div[data-baseweb="notification"][kind="positive"] {
        background-color: #d1fae5;
        border-left: 5px solid #10b981;
    }
    div[data-baseweb="notification"][kind="negative"] {
        background-color: #fee2e2;
        border-left: 5px solid #ef4444;
    }
    div[data-baseweb="notification"][kind="warning"] {
        background-color: #fef3c7;
        border-left: 5px solid #f59e0b;
    }

    /* Divider */
    hr {
        height: 3px;
        border: none;
        margin: 2rem 0;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        border-radius: 2px;
    }

</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'strategy' not in st.session_state:
    st.session_state.strategy = {'blocks': [], 'connections': []}
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None
if 'ticker_data' not in st.session_state:
    st.session_state.ticker_data = None
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "AAPL"
if 'date_range' not in st.session_state:
    st.session_state.date_range = (
        datetime.now() - timedelta(days=365),
        datetime.now()
    )
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

# Application header
st.title("AlgoBlocks")
st.markdown("### Empower Your Trading With Algorithmic Strategies")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Strategy Builder", "Data Viewer", "Backtester", "Performance Analytics", "Paper Trading"]
)

# Sidebar - Market Data Settings
st.sidebar.markdown("---")
st.sidebar.header("Market Data Settings")
ticker_input = st.sidebar.text_input("Stock Symbol", st.session_state.selected_ticker)
start_date = st.sidebar.date_input(
    "Start Date",
    st.session_state.date_range[0]
)
end_date = st.sidebar.date_input(
    "End Date",
    st.session_state.date_range[1]
)

# Update ticker data when input changes
if ticker_input != st.session_state.selected_ticker or \
   start_date != st.session_state.date_range[0] or \
   end_date != st.session_state.date_range[1]:
    
    with st.spinner(f"Loading data for {ticker_input}..."):
        try:
            data = yf.download(ticker_input, start=start_date, end=end_date)
            if not data.empty:
                st.session_state.ticker_data = data
                st.session_state.selected_ticker = ticker_input
                st.session_state.date_range = (start_date, end_date)
                st.sidebar.success(f"Data loaded for {ticker_input}")
            else:
                st.sidebar.error(f"No data available for {ticker_input}")
        except Exception as e:
            st.sidebar.error(f"Error loading data: {e}")

# Simple placeholders for our component pages
def display_strategy_builder():
    st.header("Strategy Builder")
    st.subheader("Create Trading Strategies with Blocks")
    
    # Initialize strategy data structure in session state if it doesn't exist
    if 'strategy' not in st.session_state:
        st.session_state.strategy = {
            'name': 'My Trading Strategy',
            'blocks': [],
            'connections': []
        }
    
    # Strategy information
    col1, col2 = st.columns([3, 1])
    with col1:
        strategy_name = st.text_input("Strategy Name", value=st.session_state.strategy.get('name', 'My Trading Strategy'))
    with col2:
        if st.button("Clear Strategy", key="clear_strategy"):
            st.session_state.strategy = {
                'name': strategy_name,
                'blocks': [],
                'connections': []
            }
            st.rerun()
    
    # Display saved strategy or start building a new one
    if not st.session_state.strategy.get('blocks'):
        st.info("Start by selecting a strategy type below or add blocks manually")
    
    # Available strategy types with presets
    st.markdown("### Select Strategy Type")
    strategy_type = st.selectbox("Strategy Type", 
                                ["Custom Strategy", "Moving Average Crossover", "RSI Overbought/Oversold", "MACD Signal Crossover"])
    
    # If a preset is selected, create a new strategy automatically
    if strategy_type != "Custom Strategy" and not st.session_state.strategy.get('blocks'):
        if strategy_type == "Moving Average Crossover":
            # Create a Moving Average Crossover strategy
            st.session_state.strategy = {
                'name': "Moving Average Crossover",
                'blocks': [
                    {
                        'id': 'block_1',
                        'type': 'indicator',
                        'name': 'Fast Moving Average',
                        'parameters': {'type': 'SMA', 'period': 10, 'applied_to': 'Close'}
                    },
                    {
                        'id': 'block_2',
                        'type': 'indicator',
                        'name': 'Slow Moving Average',
                        'parameters': {'type': 'SMA', 'period': 50, 'applied_to': 'Close'}
                    },
                    {
                        'id': 'block_3',
                        'type': 'comparison',
                        'name': 'Crossover Comparison',
                        'parameters': {'operator': '>', 'left': 'Fast Moving Average', 'right': 'Slow Moving Average'}
                    },
                    {
                        'id': 'block_4',
                        'type': 'order',
                        'name': 'Buy Order',
                        'parameters': {'action': 'buy', 'quantity': '100%'}
                    },
                    {
                        'id': 'block_5',
                        'type': 'comparison',
                        'name': 'Crossunder Comparison',
                        'parameters': {'operator': '<', 'left': 'Fast Moving Average', 'right': 'Slow Moving Average'}
                    },
                    {
                        'id': 'block_6',
                        'type': 'order',
                        'name': 'Sell Order',
                        'parameters': {'action': 'sell', 'quantity': '100%'}
                    }
                ],
                'connections': [
                    {'from': 'block_3', 'to': 'block_4'},
                    {'from': 'block_5', 'to': 'block_6'}
                ]
            }
            st.success("Moving Average Crossover strategy created!")
            
        elif strategy_type == "RSI Overbought/Oversold":
            # Create an RSI strategy
            st.session_state.strategy = {
                'name': "RSI Overbought/Oversold",
                'blocks': [
                    {
                        'id': 'block_1',
                        'type': 'indicator',
                        'name': 'RSI',
                        'parameters': {'period': 14, 'applied_to': 'Close'}
                    },
                    {
                        'id': 'block_2',
                        'type': 'comparison',
                        'name': 'Oversold Comparison',
                        'parameters': {'operator': '<', 'left': 'RSI', 'right': '30'}
                    },
                    {
                        'id': 'block_3',
                        'type': 'order',
                        'name': 'Buy Order',
                        'parameters': {'action': 'buy', 'quantity': '100%'}
                    },
                    {
                        'id': 'block_4',
                        'type': 'comparison',
                        'name': 'Overbought Comparison',
                        'parameters': {'operator': '>', 'left': 'RSI', 'right': '70'}
                    },
                    {
                        'id': 'block_5',
                        'type': 'order',
                        'name': 'Sell Order',
                        'parameters': {'action': 'sell', 'quantity': '100%'}
                    }
                ],
                'connections': [
                    {'from': 'block_2', 'to': 'block_3'},
                    {'from': 'block_4', 'to': 'block_5'}
                ]
            }
            st.success("RSI Overbought/Oversold strategy created!")
            
        elif strategy_type == "MACD Signal Crossover":
            # Create a MACD strategy
            st.session_state.strategy = {
                'name': "MACD Signal Crossover",
                'blocks': [
                    {
                        'id': 'block_1',
                        'type': 'indicator',
                        'name': 'MACD',
                        'parameters': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9, 'applied_to': 'Close'}
                    },
                    {
                        'id': 'block_2',
                        'type': 'comparison',
                        'name': 'MACD Crossover',
                        'parameters': {'operator': '>', 'left': 'MACD Line', 'right': 'MACD Signal'}
                    },
                    {
                        'id': 'block_3',
                        'type': 'order',
                        'name': 'Buy Order',
                        'parameters': {'action': 'buy', 'quantity': '100%'}
                    },
                    {
                        'id': 'block_4',
                        'type': 'comparison',
                        'name': 'MACD Crossunder',
                        'parameters': {'operator': '<', 'left': 'MACD Line', 'right': 'MACD Signal'}
                    },
                    {
                        'id': 'block_5',
                        'type': 'order',
                        'name': 'Sell Order',
                        'parameters': {'action': 'sell', 'quantity': '100%'}
                    }
                ],
                'connections': [
                    {'from': 'block_2', 'to': 'block_3'},
                    {'from': 'block_4', 'to': 'block_5'}
                ]
            }
            st.success("MACD Signal Crossover strategy created!")
    
    # Display current strategy blocks
    if st.session_state.strategy.get('blocks'):
        st.markdown("### Current Strategy")
        st.markdown(f"**{st.session_state.strategy.get('name', 'My Strategy')}**")
        
        # Use an expander to show the visual representation of the strategy
        with st.expander("View Strategy Blocks", expanded=True):
            # Group blocks by type for better organization
            indicators = [b for b in st.session_state.strategy['blocks'] if b['type'] == 'indicator']
            comparisons = [b for b in st.session_state.strategy['blocks'] if b['type'] == 'comparison']
            orders = [b for b in st.session_state.strategy['blocks'] if b['type'] == 'order']
            risk = [b for b in st.session_state.strategy['blocks'] if b['type'] == 'risk']
            
            # Display blocks by category
            if indicators:
                st.markdown("#### Indicators")
                for block in indicators:
                    st.markdown(
                        f"""<div style="padding: 10px; margin: 5px; border-radius: 5px; background-color: #e6f3ff; border: 1px solid #80bdff;">
                          <b>{block['name']}</b><br/>
                          <span style="font-size: 0.9em;">{', '.join([f"{k}: {v}" for k, v in block['parameters'].items()])}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
            
            if comparisons:
                st.markdown("#### Conditions")
                for block in comparisons:
                    st.markdown(
                        f"""<div style="padding: 10px; margin: 5px; border-radius: 5px; background-color: #fff3cd; border: 1px solid #ffeeba;">
                          <b>{block['name']}</b><br/>
                          <span style="font-size: 0.9em;">{block['parameters'].get('left', '')} {block['parameters'].get('operator', '')} {block['parameters'].get('right', '')}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
            
            if orders:
                st.markdown("#### Orders")
                for block in orders:
                    # Different styling for buy vs sell
                    bg_color = "#d4edda" if block['parameters'].get('action') == 'buy' else "#f8d7da"
                    border_color = "#c3e6cb" if block['parameters'].get('action') == 'buy' else "#f5c6cb"
                    
                    st.markdown(
                        f"""<div style="padding: 10px; margin: 5px; border-radius: 5px; background-color: {bg_color}; border: 1px solid {border_color};">
                          <b>{block['name']}</b><br/>
                          <span style="font-size: 0.9em;">Action: {block['parameters'].get('action', '')}, Quantity: {block['parameters'].get('quantity', '')}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
            
            if risk:
                st.markdown("#### Risk Management")
                for block in risk:
                    st.markdown(
                        f"""<div style="padding: 10px; margin: 5px; border-radius: 5px; background-color: #e2e3e5; border: 1px solid #d6d8db;">
                          <b>{block['name']}</b><br/>
                          <span style="font-size: 0.9em;">{', '.join([f"{k}: {v}" for k, v in block['parameters'].items()])}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
            
            # Display connections
            if st.session_state.strategy['connections']:
                st.markdown("#### Signal Flow")
                for conn in st.session_state.strategy['connections']:
                    from_block = next((b for b in st.session_state.strategy['blocks'] if b['id'] == conn['from']), None)
                    to_block = next((b for b in st.session_state.strategy['blocks'] if b['id'] == conn['to']), None)
                    if from_block and to_block:
                        st.markdown(f"* **{from_block['name']}** → **{to_block['name']}**")
    
    # Strategy editing options
    if st.session_state.strategy.get('blocks'):
        st.markdown("### Edit Strategy")
        
        # Block parameters
        st.subheader("Block Parameters")
        selected_block = st.selectbox("Select Block to Edit", 
                                     options=[b['id'] for b in st.session_state.strategy['blocks']],
                                     format_func=lambda x: next((b['name'] for b in st.session_state.strategy['blocks'] if b['id'] == x), ""))
        
        block = next((b for b in st.session_state.strategy['blocks'] if b['id'] == selected_block), None)
        if block:
            st.write(f"Editing: **{block['name']}**")
            
            # Create input widgets for each parameter
            updated_params = {}
            for param_name, param_value in block['parameters'].items():
                if param_name == 'period' or param_name == 'fast_period' or param_name == 'slow_period' or param_name == 'signal_period':
                    updated_params[param_name] = st.slider(f"{param_name.replace('_', ' ').title()}", 
                                                         min_value=2, max_value=200, value=int(param_value))
                elif param_name == 'type':
                    updated_params[param_name] = st.selectbox(f"{param_name.replace('_', ' ').title()}", 
                                                            options=['SMA', 'EMA', 'WMA'], index=['SMA', 'EMA', 'WMA'].index(param_value))
                elif param_name == 'operator':
                    updated_params[param_name] = st.selectbox(f"{param_name.replace('_', ' ').title()}", 
                                                            options=['>', '<', '=', '>=', '<=', '!='], index=['>', '<', '=', '>=', '<=', '!='].index(param_value))
                elif param_name == 'action':
                    updated_params[param_name] = st.selectbox(f"{param_name.replace('_', ' ').title()}", 
                                                            options=['buy', 'sell'], index=['buy', 'sell'].index(param_value))
                elif param_name == 'quantity':
                    updated_params[param_name] = st.text_input(f"{param_name.replace('_', ' ').title()}", value=param_value)
                elif param_name == 'applied_to':
                    updated_params[param_name] = st.selectbox(f"{param_name.replace('_', ' ').title()}", 
                                                            options=['Open', 'High', 'Low', 'Close'], index=['Open', 'High', 'Low', 'Close'].index(param_value))
                elif param_name == 'left' or param_name == 'right':
                    # For comparison blocks, provide a dropdown of available indicators and other values
                    indicator_names = [b['name'] for b in st.session_state.strategy['blocks'] if b['type'] == 'indicator']
                    all_options = indicator_names + ['Price', 'Open', 'High', 'Low', 'Close', 'Volume', '10', '20', '30', '40', '50', '60', '70', '80', '90']
                    
                    # Find the index of the current value or default to 0
                    try:
                        current_index = all_options.index(param_value)
                    except ValueError:
                        if param_value.isdigit() or (param_value.replace('.', '', 1).isdigit() and param_value.count('.') <= 1):
                            # It's a number but not in our default options
                            all_options.append(param_value)
                            current_index = len(all_options) - 1
                        else:
                            current_index = 0
                    
                    updated_params[param_name] = st.selectbox(f"{param_name.replace('_', ' ').title()}", 
                                                            options=all_options, index=current_index)
                else:
                    updated_params[param_name] = st.text_input(f"{param_name.replace('_', ' ').title()}", value=param_value)
            
            # Update button
            if st.button("Update Block Parameters"):
                for i, b in enumerate(st.session_state.strategy['blocks']):
                    if b['id'] == selected_block:
                        st.session_state.strategy['blocks'][i]['parameters'] = updated_params
                        st.success(f"Parameters updated for {block['name']}")
                        st.rerun()
    
    # Add new blocks section
    st.markdown("### Add New Block")
    
    # Split into tabs for different block types
    block_tabs = st.tabs(["Indicators", "Conditions", "Orders", "Risk Management"])
    
    with block_tabs[0]:  # Indicators
        st.subheader("Technical Indicators")
        indicator_type = st.selectbox("Indicator Type", ["Moving Average", "RSI", "MACD", "Bollinger Bands", "Stochastic", "ATR"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if indicator_type == "Moving Average":
                ma_type = st.selectbox("MA Type", ["SMA", "EMA", "WMA"])
                ma_period = st.slider("Period", 5, 200, 20)
                ma_applied_to = st.selectbox("Applied To", ["Close", "Open", "High", "Low", "Typical"])
                
                if st.button("Add Moving Average"):
                    new_block_id = f"block_{len(st.session_state.strategy.get('blocks', [])) + 1}"
                    new_block = {
                        'id': new_block_id,
                        'type': 'indicator',
                        'name': f"{ma_type} {ma_period}",
                        'parameters': {'type': ma_type, 'period': ma_period, 'applied_to': ma_applied_to}
                    }
                    if 'blocks' not in st.session_state.strategy:
                        st.session_state.strategy['blocks'] = []
                    st.session_state.strategy['blocks'].append(new_block)
                    st.success(f"Added {ma_type} {ma_period} indicator")
                    st.rerun()
            
            elif indicator_type == "RSI":
                rsi_period = st.slider("Period", 5, 50, 14)
                rsi_applied_to = st.selectbox("Applied To", ["Close", "Open", "High", "Low"])
                
                if st.button("Add RSI"):
                    new_block_id = f"block_{len(st.session_state.strategy.get('blocks', [])) + 1}"
                    new_block = {
                        'id': new_block_id,
                        'type': 'indicator',
                        'name': f"RSI {rsi_period}",
                        'parameters': {'period': rsi_period, 'applied_to': rsi_applied_to}
                    }
                    if 'blocks' not in st.session_state.strategy:
                        st.session_state.strategy['blocks'] = []
                    st.session_state.strategy['blocks'].append(new_block)
                    st.success(f"Added RSI {rsi_period} indicator")
                    st.rerun()
            
            elif indicator_type == "MACD":
                macd_fast = st.slider("Fast Period", 5, 50, 12)
                macd_slow = st.slider("Slow Period", 10, 100, 26)
                macd_signal = st.slider("Signal Period", 5, 40, 9)
                
                if st.button("Add MACD"):
                    new_block_id = f"block_{len(st.session_state.strategy.get('blocks', [])) + 1}"
                    new_block = {
                        'id': new_block_id,
                        'type': 'indicator',
                        'name': f"MACD {macd_fast}/{macd_slow}/{macd_signal}",
                        'parameters': {'fast_period': macd_fast, 'slow_period': macd_slow, 'signal_period': macd_signal, 'applied_to': 'Close'}
                    }
                    if 'blocks' not in st.session_state.strategy:
                        st.session_state.strategy['blocks'] = []
                    st.session_state.strategy['blocks'].append(new_block)
                    st.success(f"Added MACD indicator")
                    st.rerun()
        
        with col2:
            st.markdown("#### Indicator Description")
            if indicator_type == "Moving Average":
                st.info("Moving Averages smooth price data to identify trends. They can be used to identify support/resistance levels and trend direction.")
                st.markdown("**Parameters:**")
                st.markdown("- **Type:** Simple (SMA), Exponential (EMA), or Weighted (WMA)")
                st.markdown("- **Period:** Number of bars used in calculation")
                st.markdown("- **Applied To:** Which price data to use")
            
            elif indicator_type == "RSI":
                st.info("Relative Strength Index measures the speed and change of price movements. It identifies overbought (above 70) and oversold (below 30) conditions.")
                st.markdown("**Parameters:**")
                st.markdown("- **Period:** Number of bars used in calculation (typically 14)")
                st.markdown("- **Applied To:** Which price data to use")
            
            elif indicator_type == "MACD":
                st.info("Moving Average Convergence Divergence is a trend-following momentum indicator. It shows the relationship between two moving averages of a security's price.")
                st.markdown("**Parameters:**")
                st.markdown("- **Fast Period:** The shorter-period EMA (typically 12)")
                st.markdown("- **Slow Period:** The longer-period EMA (typically 26)")
                st.markdown("- **Signal Period:** The EMA of the MACD line (typically 9)")
    
    with block_tabs[1]:  # Conditions
        st.subheader("Comparison Conditions")
        
        # Only show comparison block creation if we have indicators to compare
        if st.session_state.strategy.get('blocks'):
            available_indicators = [b['name'] for b in st.session_state.strategy.get('blocks', []) if b['type'] == 'indicator']
            
            if available_indicators:
                col1, col2 = st.columns(2)
                
                with col1:
                    condition_name = st.text_input("Condition Name", "New Condition")
                    left_item = st.selectbox("Left Side", available_indicators + ["Price", "Open", "High", "Low", "Close"])
                    comparison_op = st.selectbox("Operator", [">", "<", "=", ">=", "<=", "!="])
                    right_item_type = st.radio("Right Side Type", ["Indicator", "Value"])
                    
                    if right_item_type == "Indicator":
                        right_item = st.selectbox("Right Side", available_indicators + ["Price", "Open", "High", "Low", "Close"])
                    else:
                        right_item = st.number_input("Value", 0.0, 100.0, 50.0)
                    
                    if st.button("Add Condition"):
                        new_block_id = f"block_{len(st.session_state.strategy.get('blocks', [])) + 1}"
                        new_block = {
                            'id': new_block_id,
                            'type': 'comparison',
                            'name': condition_name,
                            'parameters': {'left': left_item, 'operator': comparison_op, 'right': str(right_item)}
                        }
                        if 'blocks' not in st.session_state.strategy:
                            st.session_state.strategy['blocks'] = []
                        st.session_state.strategy['blocks'].append(new_block)
                        st.success(f"Added condition: {left_item} {comparison_op} {right_item}")
                        st.rerun()
                
                with col2:
                    st.markdown("#### Condition Description")
                    st.info("Comparison conditions check if a relationship between two values is true or false. They're used to generate buy/sell signals.")
                    st.markdown("**Examples:**")
                    st.markdown("- **Crossover:** 'SMA 10' > 'SMA 50'")
                    st.markdown("- **Threshold:** 'RSI 14' < '30'")
                    st.markdown("- **Price Action:** 'Close' > 'Open'")
            else:
                st.warning("Please add at least one indicator before creating conditions")
        else:
            st.warning("Please add at least one indicator before creating conditions")
    
    with block_tabs[2]:  # Orders
        st.subheader("Order Blocks")
        col1, col2 = st.columns(2)
        
        with col1:
            order_name = st.text_input("Order Name", "Order")
            order_type = st.selectbox("Order Type", ["Buy", "Sell"])
            order_quantity = st.text_input("Quantity (%)", "100%")
            
            if st.button("Add Order"):
                new_block_id = f"block_{len(st.session_state.strategy.get('blocks', [])) + 1}"
                new_block = {
                    'id': new_block_id,
                    'type': 'order',
                    'name': f"{order_type} {order_name}",
                    'parameters': {'action': order_type.lower(), 'quantity': order_quantity}
                }
                if 'blocks' not in st.session_state.strategy:
                    st.session_state.strategy['blocks'] = []
                st.session_state.strategy['blocks'].append(new_block)
                st.success(f"Added {order_type} order")
                st.rerun()
        
        with col2:
            st.markdown("#### Order Description")
            st.info("Order blocks execute trades when connected to condition blocks that evaluate to true.")
            st.markdown("**Parameters:**")
            st.markdown("- **Type:** Buy or Sell")
            st.markdown("- **Quantity:** Amount to trade (as % of available capital)")
            
    with block_tabs[3]:  # Risk Management
        st.subheader("Risk Management Blocks")
        col1, col2 = st.columns(2)
        
        with col1:
            risk_name = st.text_input("Risk Block Name", "Risk Block")
            risk_type = st.selectbox("Risk Type", ["Stop Loss", "Take Profit", "Trailing Stop"])
            risk_amount = st.text_input("Amount (%)", "2%")
            
            if st.button("Add Risk Block"):
                new_block_id = f"block_{len(st.session_state.strategy.get('blocks', [])) + 1}"
                new_block = {
                    'id': new_block_id,
                    'type': 'risk',
                    'name': f"{risk_type}",
                    'parameters': {'type': risk_type.lower().replace(' ', '_'), 'amount': risk_amount}
                }
                if 'blocks' not in st.session_state.strategy:
                    st.session_state.strategy['blocks'] = []
                st.session_state.strategy['blocks'].append(new_block)
                st.success(f"Added {risk_type} block")
                st.rerun()
        
        with col2:
            st.markdown("#### Risk Block Description")
            st.info("Risk management blocks help protect capital and lock in profits by automatically exiting positions.")
            st.markdown("**Types:**")
            st.markdown("- **Stop Loss:** Exit when loss reaches threshold")
            st.markdown("- **Take Profit:** Exit when profit reaches target")
            st.markdown("- **Trailing Stop:** Adjusts stop loss as price moves favorably")
    
    # Connection creation
    if len(st.session_state.strategy.get('blocks', [])) >= 2:
        st.markdown("### Connect Blocks")
        st.info("Create connections to define how signals flow through your strategy")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            source_options = [{'label': b['name'], 'value': b['id']} for b in st.session_state.strategy.get('blocks', []) 
                              if b['type'] in ['indicator', 'comparison']]
            source_id = st.selectbox("From", 
                                   options=[opt['value'] for opt in source_options],
                                   format_func=lambda x: next((opt['label'] for opt in source_options if opt['value'] == x), x))
        
        with col2:
            target_options = [{'label': b['name'], 'value': b['id']} for b in st.session_state.strategy.get('blocks', []) 
                              if b['type'] in ['comparison', 'order', 'risk']]
            target_id = st.selectbox("To", 
                                   options=[opt['value'] for opt in target_options],
                                   format_func=lambda x: next((opt['label'] for opt in target_options if opt['value'] == x), x))
        
        with col3:
            if st.button("Create Connection"):
                # Check if this connection already exists
                if 'connections' not in st.session_state.strategy:
                    st.session_state.strategy['connections'] = []
                
                existing_conn = next((c for c in st.session_state.strategy['connections'] 
                                    if c.get('from') == source_id and c.get('to') == target_id), None)
                
                if existing_conn:
                    st.warning("This connection already exists")
                else:
                    st.session_state.strategy['connections'].append({
                        'from': source_id,
                        'to': target_id
                    })
                    
                    source_block = next((b for b in st.session_state.strategy['blocks'] if b['id'] == source_id), None)
                    target_block = next((b for b in st.session_state.strategy['blocks'] if b['id'] == target_id), None)
                    
                    if source_block and target_block:
                        st.success(f"Connected '{source_block['name']}' to '{target_block['name']}'")
                        st.rerun()
    
    # Strategy actions - final section
    st.markdown("### Strategy Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Validate Strategy", key="validate_strategy"):
            # Perform some basic validation
            if not st.session_state.strategy.get('blocks'):
                st.error("Strategy is empty. Please add some blocks.")
            elif not st.session_state.strategy.get('connections'):
                st.warning("Strategy has no connections between blocks.")
            else:
                # Check if there are order blocks
                has_orders = any(b['type'] == 'order' for b in st.session_state.strategy.get('blocks', []))
                if not has_orders:
                    st.warning("Strategy has no order blocks. It will not execute any trades.")
                else:
                    st.success("Strategy validation successful!")
    
    with col2:
        if st.button("Save Strategy", key="save_strategy"):
            # Save strategy name
            st.session_state.strategy['name'] = strategy_name
            st.success(f"Strategy '{strategy_name}' saved successfully!")
            
            # In a real app, this would save to a file or database

def display_data_viewer():
    st.header("Market Data Viewer")
    
    if st.session_state.ticker_data is None:
        st.warning("Please load a ticker from the sidebar to view market data.")
        return
    
    # Data overview
    data = st.session_state.ticker_data
    ticker = st.session_state.selected_ticker
    
    st.subheader(f"{ticker} Price Data")
    
    # Date range summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Start Date", data.index[0].strftime('%Y-%m-%d'))
    with col2:
        st.metric("End Date", data.index[-1].strftime('%Y-%m-%d'))
    with col3:
        st.metric("Days", f"{len(data)}")
    
    # Price summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"${float(data['Close'].iloc[-1]):.2f}")
    with col2:
        price_change = float(data['Close'].iloc[-1]) - float(data['Close'].iloc[0])
        percent_change = (price_change / float(data['Close'].iloc[0])) * 100
        st.metric("Price Change", f"${price_change:.2f}", f"{percent_change:.2f}%")
    with col3:
        st.metric("High", f"${float(data['High'].max()):.2f}")
    with col4:
        st.metric("Low", f"${float(data['Low'].min()):.2f}")
    
    # Price chart
    st.subheader("Price Chart")
    show_volume = st.checkbox("Show Volume", value=True)
    
    # Indicators selection
    indicators_expander = st.expander("Add Technical Indicators")
    with indicators_expander:
        col1, col2, col3 = st.columns(3)
        with col1:
            show_sma = st.checkbox("SMA", value=True)
            sma_period = st.slider("SMA Period", 5, 200, 20) if show_sma else 20
        with col2:
            show_ema = st.checkbox("EMA", value=False)
            ema_period = st.slider("EMA Period", 5, 200, 20) if show_ema else 20
        with col3:
            show_bb = st.checkbox("Bollinger Bands", value=False)
            bb_period = st.slider("BB Period", 5, 50, 20) if show_bb else 20
    
    # Create the figure
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price'
        )
    )
    
    # Add SMA if selected
    if show_sma:
        sma = data['Close'].rolling(window=sma_period).mean()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=sma,
                mode='lines',
                name=f'SMA ({sma_period})',
                line=dict(color='blue', width=1)
            )
        )
    
    # Add EMA if selected
    if show_ema:
        ema = data['Close'].ewm(span=ema_period, adjust=False).mean()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=ema,
                mode='lines',
                name=f'EMA ({ema_period})',
                line=dict(color='orange', width=1)
            )
        )
    
    # Add Bollinger Bands if selected
    if show_bb:
        sma = data['Close'].rolling(window=bb_period).mean()
        std = data['Close'].rolling(window=bb_period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=upper_band,
                mode='lines',
                name='Upper BB',
                line=dict(color='rgba(0,128,0,0.3)', width=1)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=sma,
                mode='lines',
                name='Middle BB',
                line=dict(color='rgba(0,128,0,0.8)', width=1)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=lower_band,
                mode='lines',
                name='Lower BB',
                line=dict(color='rgba(0,128,0,0.3)', width=1),
                fill='tonexty',
                fillcolor='rgba(0,128,0,0.05)'
            )
        )
    
    # Add volume if selected
    if show_volume:
        # Create volume trace
        colors = []
        for i in range(len(data)):
            if float(data['Close'].iloc[i]) < float(data['Open'].iloc[i]):
                colors.append('red')
            else:
                colors.append('green')
        
        # Add subplot for volume
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.5,
                yaxis='y2'
            )
        )
        
        # Update layout for secondary y-axis
        fig.update_layout(
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False
            )
        )
    
    # Update layout
    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=600,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("Raw Data")
    st.dataframe(data)

def display_backtester():
    st.header("Backtest Your Strategy")
    
    if st.session_state.ticker_data is None:
        st.warning("Please load a ticker from the sidebar to run a backtest.")
        return
    
    # Backtest parameters
    st.subheader("Backtest Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        initial_capital = st.number_input("Initial Capital ($)", min_value=100.0, max_value=1000000.0, value=10000.0, step=1000.0)
        commission = st.number_input("Commission (%)", min_value=0.0, max_value=5.0, value=0.1, step=0.05) / 100
    
    with col2:
        # Select strategy
        strategy_options = ["Simple Moving Average Crossover", "RSI Strategy", "MACD Strategy", "Custom Strategy"]
        selected_strategy = st.selectbox("Select Strategy", strategy_options)
        
        # Strategy parameters
        if selected_strategy == "Simple Moving Average Crossover":
            fast_period = st.slider("Fast SMA Period", 5, 50, 10)
            slow_period = st.slider("Slow SMA Period", 10, 200, 50)
            
            # Create strategy logic for backtest
            strategy = {
                "name": selected_strategy,
                "parameters": {
                    "fast_period": fast_period,
                    "slow_period": slow_period
                }
            }
        elif selected_strategy == "RSI Strategy":
            rsi_period = st.slider("RSI Period", 5, 50, 14)
            oversold = st.slider("Oversold Level", 10, 40, 30)
            overbought = st.slider("Overbought Level", 60, 90, 70)
            
            # Create strategy logic for backtest
            strategy = {
                "name": selected_strategy,
                "parameters": {
                    "rsi_period": rsi_period,
                    "oversold": oversold,
                    "overbought": overbought
                }
            }
        elif selected_strategy == "MACD Strategy":
            fast_period = st.slider("Fast EMA Period", 5, 50, 12)
            slow_period = st.slider("Slow EMA Period", 10, 100, 26)
            signal_period = st.slider("Signal Period", 5, 50, 9)
            
            # Create strategy logic for backtest
            strategy = {
                "name": selected_strategy,
                "parameters": {
                    "fast_period": fast_period,
                    "slow_period": slow_period,
                    "signal_period": signal_period
                }
            }
        else:
            st.info("Please build a custom strategy in the Strategy Builder tab")
            strategy = st.session_state.strategy if st.session_state.strategy else None
    
    # Run backtest button
    if st.button("Run Backtest", key="run_backtest", disabled=(strategy is None)):
        with st.spinner("Running backtest..."):
            # Simulate backtest calculation
            time.sleep(2)
            
            # Create simulated backtest results
            data = st.session_state.ticker_data
            ticker = st.session_state.selected_ticker
            
            # Initialize buy and sell signals as empty series
            buy_signals = pd.Series(False, index=data.index)
            sell_signals = pd.Series(False, index=data.index)
            
            # Simulate strategy signals and execution
            # This is a placeholder - in a real app, you would run actual backtest logic based on the strategy
            if selected_strategy == "Simple Moving Average Crossover":
                fast_ma = data['Close'].rolling(window=strategy['parameters']['fast_period']).mean()
                slow_ma = data['Close'].rolling(window=strategy['parameters']['slow_period']).mean()
                
                # Generate buy signals when fast MA crosses above slow MA
                for i in range(1, len(data)):
                    if float(fast_ma.iloc[i]) > float(slow_ma.iloc[i]) and float(fast_ma.iloc[i-1]) <= float(slow_ma.iloc[i-1]):
                        buy_signals.iloc[i] = True
                    if float(fast_ma.iloc[i]) < float(slow_ma.iloc[i]) and float(fast_ma.iloc[i-1]) >= float(slow_ma.iloc[i-1]):
                        sell_signals.iloc[i] = True
            
            elif selected_strategy == "RSI Strategy":
                # Calculate RSI
                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(window=strategy['parameters']['rsi_period']).mean()
                avg_loss = loss.rolling(window=strategy['parameters']['rsi_period']).mean()
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                
                # Generate buy signals when RSI crosses below oversold level
                for i in range(1, len(data)):
                    if float(rsi.iloc[i]) < strategy['parameters']['oversold'] and float(rsi.iloc[i-1]) >= strategy['parameters']['oversold']:
                        buy_signals.iloc[i] = True
                    if float(rsi.iloc[i]) > strategy['parameters']['overbought'] and float(rsi.iloc[i-1]) <= strategy['parameters']['overbought']:
                        sell_signals.iloc[i] = True
            
            elif selected_strategy == "MACD Strategy":
                # Calculate MACD
                ema_fast = data['Close'].ewm(span=strategy['parameters']['fast_period'], adjust=False).mean()
                ema_slow = data['Close'].ewm(span=strategy['parameters']['slow_period'], adjust=False).mean()
                macd_line = ema_fast - ema_slow
                signal_line = macd_line.ewm(span=strategy['parameters']['signal_period'], adjust=False).mean()
                
                # Generate buy signals when MACD crosses above signal line
                for i in range(1, len(data)):
                    if float(macd_line.iloc[i]) > float(signal_line.iloc[i]) and float(macd_line.iloc[i-1]) <= float(signal_line.iloc[i-1]):
                        buy_signals.iloc[i] = True
                    if float(macd_line.iloc[i]) < float(signal_line.iloc[i]) and float(macd_line.iloc[i-1]) >= float(signal_line.iloc[i-1]):
                        sell_signals.iloc[i] = True
            
            else:
                # Use the custom strategy from the Strategy Builder
                if st.session_state.strategy and 'blocks' in st.session_state.strategy:
                    # This is a very simplified implementation - in a real app, you would interpret
                    # the block logic and apply it to the data
                    st.info("Using custom strategy from Strategy Builder")
                    
                    # Generate some basic signals for demonstration
                    for i in range(5, len(data), 20):  # Buy every 20 days
                        if i < len(data):
                            buy_signals.iloc[i] = True
                    
                    for i in range(15, len(data), 20):  # Sell every 20 days (10 days after buy)
                        if i < len(data):
                            sell_signals.iloc[i] = True
                else:
                    # Default to random signals for demonstration
                    np.random.seed(42)  # For reproducibility
                    random_signals = np.random.random(len(data))
                    
                    for i in range(len(data)):
                        if random_signals[i] < 0.03:
                            buy_signals.iloc[i] = True
                        if random_signals[i] > 0.97:
                            sell_signals.iloc[i] = True
            
            # Simulate equity curve
            equity = pd.Series(initial_capital, index=data.index)
            position = 0
            entry_price = 0
            trades = []
            
            for i in range(1, len(data)):
                # If we have a buy signal and no position
                if buy_signals.iloc[i] and position == 0:
                    entry_price = float(data['Close'].iloc[i])
                    # Calculate position size (simplified)
                    position = float(equity.iloc[i-1]) / entry_price
                    trades.append({
                        'type': 'buy',
                        'date': data.index[i],
                        'price': entry_price,
                        'shares': position
                    })
                
                # If we have a sell signal and have a position
                elif sell_signals.iloc[i] and position > 0:
                    exit_price = float(data['Close'].iloc[i])
                    # Calculate profit/loss
                    pnl = position * (exit_price - entry_price)
                    # Subtract commission
                    pnl -= (position * entry_price + position * exit_price) * commission
                    
                    # Update equity
                    equity.iloc[i] = equity.iloc[i-1] + pnl
                    
                    trades.append({
                        'type': 'sell',
                        'date': data.index[i],
                        'price': exit_price,
                        'shares': position,
                        'pnl': pnl
                    })
                    
                    position = 0
                    entry_price = 0
                
                # No trade, equity stays the same
                else:
                    if position > 0:
                        # Update equity with unrealized gains/losses
                        current_value = position * float(data['Close'].iloc[i])
                        equity.iloc[i] = equity.iloc[i-1] + (position * (float(data['Close'].iloc[i]) - float(data['Close'].iloc[i-1])))
                    else:
                        equity.iloc[i] = equity.iloc[i-1]
            
            # Calculate performance metrics
            total_return = (equity.iloc[-1] - initial_capital) / initial_capital * 100
            annual_return = total_return / (len(data) / 252) # Assuming 252 trading days per year
            max_drawdown = ((equity.cummax() - equity) / equity.cummax()).max() * 100
            win_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
            total_trades = sum(1 for trade in trades if trade.get('type') == 'sell')
            win_rate = win_trades / total_trades if total_trades > 0 else 0
            
            # Create a results dictionary
            backtest_results = {
                'strategy': strategy['name'],
                'ticker': ticker,
                'initial_capital': initial_capital,
                'final_equity': equity.iloc[-1],
                'total_return': total_return,
                'annual_return': annual_return,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate * 100,
                'total_trades': total_trades,
                'equity_curve': equity,
                'trades': trades,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals
            }
            
            # Store results in session state
            st.session_state.backtest_results = backtest_results
    
    # Display backtest results
    if st.session_state.backtest_results:
        results = st.session_state.backtest_results
        
        st.subheader("Backtest Results")
        
        # Performance summary cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Return", f"{results['total_return']:.2f}%", f"${results['final_equity']-results['initial_capital']:.2f}")
        with col2:
            st.metric("Annual Return", f"{results['annual_return']:.2f}%")
        with col3:
            st.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
        with col4:
            st.metric("Win Rate", f"{results['win_rate']:.2f}%", f"{results['total_trades']} trades")
        
        # Equity curve
        st.subheader("Equity Curve")
        equity_fig = go.Figure()
        equity_fig.add_trace(
            go.Scatter(
                x=results['equity_curve'].index,
                y=results['equity_curve'].values,
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2)
            )
        )
        
        # Buy and sell markers on equity curve
        buy_dates = [trade['date'] for trade in results['trades'] if trade['type'] == 'buy']
        buy_values = [results['equity_curve'].loc[date] for date in buy_dates]
        
        sell_dates = [trade['date'] for trade in results['trades'] if trade['type'] == 'sell']
        sell_values = [results['equity_curve'].loc[date] for date in sell_dates]
        
        equity_fig.add_trace(
            go.Scatter(
                x=buy_dates,
                y=buy_values,
                mode='markers',
                name='Buy',
                marker=dict(color='green', size=8, symbol='triangle-up')
            )
        )
        
        equity_fig.add_trace(
            go.Scatter(
                x=sell_dates,
                y=sell_values,
                mode='markers',
                name='Sell',
                marker=dict(color='red', size=8, symbol='triangle-down')
            )
        )
        
        equity_fig.update_layout(
            title=f"Equity Curve - {results['strategy']} on {results['ticker']}",
            xaxis_title="Date",
            yaxis_title="Equity ($)",
            height=400,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(equity_fig, use_container_width=True)
        
        # Trade list
        st.subheader("Trade History")
        
        if results['trades']:
            trade_data = []
            for trade in results['trades']:
                if trade['type'] == 'sell':  # Only show completed trades
                    # Find the corresponding buy trade
                    buy_trade = next((t for t in results['trades'] if t['type'] == 'buy' and t['shares'] == trade['shares'] and t['date'] < trade['date']), None)
                    if buy_trade:
                        trade_data.append({
                            'Entry Date': buy_trade['date'].strftime('%Y-%m-%d'),
                            'Entry Price': f"${buy_trade['price']:.2f}",
                            'Exit Date': trade['date'].strftime('%Y-%m-%d'),
                            'Exit Price': f"${trade['price']:.2f}",
                            'Shares': f"{trade['shares']:.2f}",
                            'P&L': f"${trade['pnl']:.2f}",
                            'Return': f"{(trade['pnl'] / (buy_trade['price'] * trade['shares'])) * 100:.2f}%"
                        })
            
            if trade_data:
                st.dataframe(pd.DataFrame(trade_data))
            else:
                st.info("No completed trades in this backtest.")
        else:
            st.info("No trades were executed in this backtest.")

def display_performance_dashboard():
    st.header("Performance Analytics")
    
    if st.session_state.backtest_results is None:
        st.warning("Please run a backtest first to view performance analytics.")
        return
    
    # Get backtest results
    results = st.session_state.backtest_results
    
    # Overview
    st.subheader("Strategy Performance Overview")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Strategy", results['strategy'])
        st.metric("Ticker", results['ticker'])
        st.metric("Initial Capital", f"${results['initial_capital']:.2f}")
        st.metric("Final Equity", f"${results['final_equity']:.2f}")
    
    with col2:
        st.metric("Total Return", f"{results['total_return']:.2f}%")
        st.metric("Annual Return", f"{results['annual_return']:.2f}%")
        st.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
        st.metric("Win Rate", f"{results['win_rate']:.2f}%")
    
    # Detailed metrics
    st.subheader("Detailed Performance Metrics")
    
    # Calculate monthly returns
    equity_curve = results['equity_curve']
    equity_curve.index = pd.to_datetime(equity_curve.index)
    monthly_returns = equity_curve.resample('M').last().pct_change().dropna()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly returns heatmap
        if not monthly_returns.empty and len(monthly_returns) > 1:
            # Prepare data for heatmap
            monthly_returns_pivot = monthly_returns.copy()
            monthly_returns_pivot.index = monthly_returns_pivot.index.strftime('%Y-%m')
            
            # Create a bar chart for monthly returns
            monthly_fig = go.Figure()
            monthly_fig.add_trace(
                go.Bar(
                    x=monthly_returns_pivot.index,
                    y=monthly_returns_pivot.values * 100,
                    marker_color=['red' if x < 0 else 'green' for x in monthly_returns_pivot.values],
                    name='Monthly Return'
                )
            )
            
            monthly_fig.update_layout(
                title="Monthly Returns (%)",
                xaxis_title="Month",
                yaxis_title="Return (%)",
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            st.plotly_chart(monthly_fig, use_container_width=True)
        else:
            st.info("Not enough data to calculate monthly returns.")
    
    with col2:
        # Drawdown chart
        if len(equity_curve) > 1:
            # Calculate drawdown
            peak = equity_curve.cummax()
            drawdown = (equity_curve - peak) / peak * 100
            
            drawdown_fig = go.Figure()
            drawdown_fig.add_trace(
                go.Scatter(
                    x=drawdown.index,
                    y=drawdown.values,
                    fill='tozeroy',
                    fillcolor='rgba(255,0,0,0.2)',
                    line=dict(color='red', width=1),
                    name='Drawdown'
                )
            )
            
            drawdown_fig.update_layout(
                title="Drawdown (%)",
                xaxis_title="Date",
                yaxis_title="Drawdown (%)",
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            st.plotly_chart(drawdown_fig, use_container_width=True)
        else:
            st.info("Not enough data to calculate drawdown.")
    
    # Trade analysis
    st.subheader("Trade Analysis")
    
    if results['trades']:
        # Extract trades data
        pnl_values = [trade.get('pnl', 0) for trade in results['trades'] if trade.get('type') == 'sell']
        
        if pnl_values:
            # Profit/Loss distribution
            pnl_fig = go.Figure()
            pnl_fig.add_trace(
                go.Histogram(
                    x=pnl_values,
                    marker_color=['red' if x < 0 else 'green' for x in pnl_values],
                    name='P&L Distribution'
                )
            )
            
            pnl_fig.update_layout(
                title="Profit/Loss Distribution",
                xaxis_title="P&L ($)",
                yaxis_title="Frequency",
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            st.plotly_chart(pnl_fig, use_container_width=True)
            
            # Calculate profit metrics
            avg_profit = sum(pnl for pnl in pnl_values if pnl > 0) / sum(1 for pnl in pnl_values if pnl > 0) if any(pnl > 0 for pnl in pnl_values) else 0
            avg_loss = sum(pnl for pnl in pnl_values if pnl < 0) / sum(1 for pnl in pnl_values if pnl < 0) if any(pnl < 0 for pnl in pnl_values) else 0
            profit_factor = abs(sum(pnl for pnl in pnl_values if pnl > 0) / sum(pnl for pnl in pnl_values if pnl < 0)) if sum(pnl for pnl in pnl_values if pnl < 0) != 0 else float('inf')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Profit", f"${avg_profit:.2f}")
            with col2:
                st.metric("Average Loss", f"${avg_loss:.2f}")
            with col3:
                st.metric("Profit Factor", f"{profit_factor:.2f}")
            
        else:
            st.info("No completed trades with P&L information.")
    else:
        st.info("No trades were executed in this backtest.")

def display_paper_trading():
    st.header("Paper Trading Simulation")
    
    if st.session_state.ticker_data is None:
        st.warning("Please load a ticker from the sidebar to start paper trading.")
        return
    
    # Paper trading parameters
    st.subheader("Paper Trading Setup")
    
    col1, col2 = st.columns(2)
    with col1:
        initial_capital = st.number_input("Initial Capital ($)", min_value=100.0, max_value=1000000.0, value=10000.0, step=1000.0, key="paper_capital")
        commission = st.number_input("Commission (%)", min_value=0.0, max_value=5.0, value=0.1, step=0.05, key="paper_commission") / 100
    
    with col2:
        # Select strategy
        strategy_options = ["Simple Moving Average Crossover", "RSI Strategy", "MACD Strategy", "Custom Strategy"]
        selected_strategy = st.selectbox("Select Strategy", strategy_options, key="paper_strategy")
        
        # Strategy parameters (similar to backtester)
        if selected_strategy == "Simple Moving Average Crossover":
            fast_period = st.slider("Fast SMA Period", 5, 50, 10, key="paper_fast_sma")
            slow_period = st.slider("Slow SMA Period", 10, 200, 50, key="paper_slow_sma")
            
            # Create strategy logic
            strategy = {
                "name": selected_strategy,
                "parameters": {
                    "fast_period": fast_period,
                    "slow_period": slow_period
                }
            }
        elif selected_strategy == "RSI Strategy":
            rsi_period = st.slider("RSI Period", 5, 50, 14, key="paper_rsi")
            oversold = st.slider("Oversold Level", 10, 40, 30, key="paper_oversold")
            overbought = st.slider("Overbought Level", 60, 90, 70, key="paper_overbought")
            
            # Create strategy logic
            strategy = {
                "name": selected_strategy,
                "parameters": {
                    "rsi_period": rsi_period,
                    "oversold": oversold,
                    "overbought": overbought
                }
            }
        elif selected_strategy == "MACD Strategy":
            fast_period = st.slider("Fast EMA Period", 5, 50, 12, key="paper_fast_ema")
            slow_period = st.slider("Slow EMA Period", 10, 100, 26, key="paper_slow_ema")
            signal_period = st.slider("Signal Period", 5, 50, 9, key="paper_signal")
            
            # Create strategy logic
            strategy = {
                "name": selected_strategy,
                "parameters": {
                    "fast_period": fast_period,
                    "slow_period": slow_period,
                    "signal_period": signal_period
                }
            }
        else:
            st.info("Please build a custom strategy in the Strategy Builder tab")
            strategy = st.session_state.strategy if st.session_state.strategy else None
    
    # Start simulation button
    if st.button("Start Paper Trading Simulation", key="start_paper", disabled=(strategy is None)):
        with st.spinner("Setting up paper trading simulation..."):
            # Simulate paper trading setup
            time.sleep(2)
            
            # Use data from the backtest function but with some adjustments for paper trading
            data = st.session_state.ticker_data
            ticker = st.session_state.selected_ticker
            
            # In real implementation, this would use a different mechanism to generate signals in real-time
            # Here we just use the same approach as the backtest for demonstration
            if selected_strategy == "Simple Moving Average Crossover":
                fast_ma = data['Close'].rolling(window=strategy['parameters']['fast_period']).mean()
                slow_ma = data['Close'].rolling(window=strategy['parameters']['slow_period']).mean()
                
                # Generate buy signals when fast MA crosses above slow MA
                buy_signals = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
                
                # Generate sell signals when fast MA crosses below slow MA
                sell_signals = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
            
            elif selected_strategy == "RSI Strategy":
                # Calculate RSI
                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(window=strategy['parameters']['rsi_period']).mean()
                avg_loss = loss.rolling(window=strategy['parameters']['rsi_period']).mean()
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                
                # Generate buy signals when RSI crosses below oversold level
                buy_signals = (rsi < strategy['parameters']['oversold']) & (rsi.shift(1) >= strategy['parameters']['oversold'])
                
                # Generate sell signals when RSI crosses above overbought level
                sell_signals = (rsi > strategy['parameters']['overbought']) & (rsi.shift(1) <= strategy['parameters']['overbought'])
            
            elif selected_strategy == "MACD Strategy":
                # Calculate MACD
                ema_fast = data['Close'].ewm(span=strategy['parameters']['fast_period'], adjust=False).mean()
                ema_slow = data['Close'].ewm(span=strategy['parameters']['slow_period'], adjust=False).mean()
                macd_line = ema_fast - ema_slow
                signal_line = macd_line.ewm(span=strategy['parameters']['signal_period'], adjust=False).mean()
                
                # Generate buy signals when MACD crosses above signal line
                buy_signals = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
                
                # Generate sell signals when MACD crosses below signal line
                sell_signals = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))
            
            else:
                # Default to random signals for demonstration
                np.random.seed(42)  # For reproducibility
                random_signals = np.random.random(len(data))
                buy_signals = pd.Series(random_signals < 0.03, index=data.index)
                sell_signals = pd.Series(random_signals > 0.97, index=data.index)
            
            # Create a paper trading simulation (similar to backtest but with different labels)
            equity = pd.Series(initial_capital, index=data.index)
            position = 0
            entry_price = 0
            trades = []
            
            # For paper trading, we'll only use the last 30 days of data to simulate recent trading
            simulation_start = max(0, len(data) - 30)
            
            for i in range(simulation_start, len(data)):
                # If we have a buy signal and no position
                if buy_signals.iloc[i] == True and position == 0:
                    entry_price = float(data['Close'].iloc[i])
                    position = float(equity.iloc[i-1]) / entry_price
                    trades.append({
                        'type': 'buy',
                        'date': data.index[i],
                        'price': entry_price,
                        'shares': position
                    })
                
                # If we have a sell signal and have a position
                elif sell_signals.iloc[i] == True and position > 0:
                    exit_price = float(data['Close'].iloc[i])
                    pnl = position * (exit_price - entry_price)
                    pnl -= (position * entry_price + position * exit_price) * commission
                    
                    equity.iloc[i] = equity.iloc[i-1] + pnl
                    
                    trades.append({
                        'type': 'sell',
                        'date': data.index[i],
                        'price': exit_price,
                        'shares': position,
                        'pnl': pnl
                    })
                    
                    position = 0
                    entry_price = 0
                
                # No trade, equity stays the same
                else:
                    if position > 0:
                        # Update equity with unrealized gains/losses
                        equity.iloc[i] = equity.iloc[i-1] + (position * (float(data['Close'].iloc[i]) - float(data['Close'].iloc[i-1])))
                    else:
                        equity.iloc[i] = equity.iloc[i-1]
            
            # Calculate performance metrics
            final_equity = float(equity.iloc[-1])
            total_return = (final_equity - initial_capital) / initial_capital * 100
            current_position = position
            current_position_value = position * float(data['Close'].iloc[-1]) if position > 0 else 0
            
            # Only include trades from the paper trading period
            paper_trades = [trade for trade in trades if trade['date'] >= data.index[simulation_start]]
            total_trades = sum(1 for trade in paper_trades if trade.get('type') == 'sell')
            win_trades = sum(1 for trade in paper_trades if trade.get('type') == 'sell' and trade.get('pnl', 0) > 0)
            win_rate = win_trades / total_trades if total_trades > 0 else 0
            
            # Create a results dictionary
            simulation_results = {
                'strategy': strategy['name'],
                'ticker': ticker,
                'initial_capital': initial_capital,
                'final_equity': final_equity,
                'total_return': total_return,
                'current_position': current_position,
                'current_position_value': current_position_value,
                'entry_price': entry_price if position > 0 else 0,
                'latest_price': float(data['Close'].iloc[-1]),
                'win_rate': win_rate * 100,
                'total_trades': total_trades,
                'equity_curve': equity[simulation_start:],
                'trades': paper_trades
            }
            
            # Store results in session state
            st.session_state.simulation_results = simulation_results
    
    # Display paper trading results
    if st.session_state.simulation_results:
        results = st.session_state.simulation_results
        
        st.subheader("Paper Trading Dashboard")
        
        # Account overview
        st.markdown("#### Account Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Equity", f"${results['final_equity']:.2f}", f"{results['total_return']:.2f}%")
        
        with col2:
            position_value = results['current_position_value']
            unrealized_pnl = position_value - (results['current_position'] * results['entry_price']) if results['current_position'] > 0 else 0
            unrealized_percent = (unrealized_pnl / (results['current_position'] * results['entry_price'])) * 100 if results['current_position'] > 0 else 0
            
            st.metric("Position Value", f"${position_value:.2f}", f"{unrealized_percent:.2f}%" if unrealized_percent != 0 else None)
        
        with col3:
            st.metric("Available Cash", f"${results['final_equity'] - position_value:.2f}")
        
        with col4:
            st.metric("Win Rate", f"{results['win_rate']:.2f}%", f"{results['total_trades']} trades")
        
        # Current position
        st.markdown("#### Current Position")
        
        if results['current_position'] > 0:
            position_data = {
                'Ticker': results['ticker'],
                'Shares': f"{results['current_position']:.2f}",
                'Entry Price': f"${results['entry_price']:.2f}",
                'Current Price': f"${results['latest_price']:.2f}",
                'Market Value': f"${position_value:.2f}",
                'Unrealized P&L': f"${unrealized_pnl:.2f} ({unrealized_percent:.2f}%)"
            }
            
            position_df = pd.DataFrame([position_data])
            st.dataframe(position_df)
        else:
            st.info("No open positions.")
        
        # Equity curve
        st.markdown("#### Equity Curve")
        
        equity_fig = go.Figure()
        equity_fig.add_trace(
            go.Scatter(
                x=results['equity_curve'].index,
                y=results['equity_curve'].values,
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2)
            )
        )
        
        # Buy and sell markers on equity curve
        buy_dates = [trade['date'] for trade in results['trades'] if trade['type'] == 'buy']
        buy_values = [results['equity_curve'].loc[date] for date in buy_dates if date in results['equity_curve'].index]
        buy_dates = [date for date in buy_dates if date in results['equity_curve'].index]
        
        sell_dates = [trade['date'] for trade in results['trades'] if trade['type'] == 'sell']
        sell_values = [results['equity_curve'].loc[date] for date in sell_dates if date in results['equity_curve'].index]
        sell_dates = [date for date in sell_dates if date in results['equity_curve'].index]
        
        if buy_dates:
            equity_fig.add_trace(
                go.Scatter(
                    x=buy_dates,
                    y=buy_values,
                    mode='markers',
                    name='Buy',
                    marker=dict(color='green', size=8, symbol='triangle-up')
                )
            )
        
        if sell_dates:
            equity_fig.add_trace(
                go.Scatter(
                    x=sell_dates,
                    y=sell_values,
                    mode='markers',
                    name='Sell',
                    marker=dict(color='red', size=8, symbol='triangle-down')
                )
            )
        
        equity_fig.update_layout(
            title=f"Paper Trading Equity Curve - {results['strategy']} on {results['ticker']}",
            xaxis_title="Date",
            yaxis_title="Equity ($)",
            height=400,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(equity_fig, use_container_width=True)
        
        # Trade history
        st.markdown("#### Trade History")
        
        if results['trades']:
            trade_data = []
            for trade in results['trades']:
                if trade['type'] == 'sell':  # Only show completed trades
                    # Find the corresponding buy trade
                    buy_trade = next((t for t in results['trades'] if t['type'] == 'buy' and t['shares'] == trade['shares'] and t['date'] < trade['date']), None)
                    if buy_trade:
                        trade_data.append({
                            'Entry Date': buy_trade['date'].strftime('%Y-%m-%d'),
                            'Entry Price': f"${buy_trade['price']:.2f}",
                            'Exit Date': trade['date'].strftime('%Y-%m-%d'),
                            'Exit Price': f"${trade['price']:.2f}",
                            'Shares': f"{trade['shares']:.2f}",
                            'P&L': f"${trade['pnl']:.2f}",
                            'Return': f"{(trade['pnl'] / (buy_trade['price'] * trade['shares'])) * 100:.2f}%"
                        })
            
            if trade_data:
                st.dataframe(pd.DataFrame(trade_data))
            else:
                st.info("No completed trades in this simulation.")
        else:
            st.info("No trades were executed in this simulation.")
        
        # Order entry
        st.markdown("#### Manual Order Entry")
        st.markdown("Override your strategy with manual orders:")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            order_type = st.selectbox("Order Type", ["Market Buy", "Market Sell", "Limit Buy", "Limit Sell"])
        
        with col2:
            if "Limit" in order_type:
                limit_price = st.number_input("Limit Price", min_value=0.01, value=results['latest_price'], step=0.01)
            else:
                st.metric("Current Price", f"${results['latest_price']:.2f}")
        
        with col3:
            # For simplicity, let's just use dollars instead of shares
            order_value = st.number_input("Order Value ($)", min_value=10.0, max_value=results['final_equity'], value=1000.0, step=100.0)
            shares = order_value / results['latest_price']
        
        with col4:
            st.metric("Shares", f"{shares:.2f}")
            st.button("Place Order", key="place_order")
        
        st.info("Note: Manual orders are simulated and not actually executed. In a production system, this would integrate with a brokerage API.")

# Page content based on navigation
if page == "Strategy Builder":
    display_strategy_builder()
elif page == "Data Viewer":
    display_data_viewer()
elif page == "Backtester":
    display_backtester()
elif page == "Performance Analytics":
    display_performance_dashboard()
elif page == "Paper Trading":
    display_paper_trading()

# Footer
st.markdown("---")
st.markdown("**AlgoBlocks** - Democratizing Algorithmic Trading | Built with Streamlit")