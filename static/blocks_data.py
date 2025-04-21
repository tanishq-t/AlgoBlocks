"""
Predefined block data for AlgoBlocks

This module provides structured data for the blocks available in the application,
including their configurations, parameters, and constraints.
"""

# Block Categories
BLOCK_CATEGORIES = [
    "Data Inputs",
    "Indicators",
    "Entry Conditions",
    "Exit Conditions",
    "Risk Management",
    "Order Execution"
]

# Blocks by Category
BLOCKS_BY_CATEGORY = {
    "Data Inputs": [
        {
            "id": "price_data",
            "name": "Price Data",
            "description": "OHLCV price data from the selected ticker",
            "inputs": [],
            "outputs": ["Open", "High", "Low", "Close", "Volume"],
            "icon": "database"
        },
        {
            "id": "timeframe",
            "name": "Timeframe",
            "description": "Select timeframe for analysis",
            "inputs": [],
            "outputs": ["timeframe"],
            "params": {
                "timeframe": {
                    "type": "select",
                    "options": ["1d", "1w", "1m"],
                    "default": "1d"
                }
            },
            "icon": "clock"
        },
        {
            "id": "market_data_filter",
            "name": "Data Filter",
            "description": "Filter market data by date range",
            "inputs": ["data"],
            "outputs": ["filtered_data"],
            "params": {
                "start_date_offset": {
                    "type": "number",
                    "min": 0,
                    "max": 1000,
                    "default": 100,
                    "description": "Start date offset in days from current date"
                },
                "end_date_offset": {
                    "type": "number",
                    "min": 0,
                    "max": 100,
                    "default": 0,
                    "description": "End date offset in days from current date"
                }
            },
            "icon": "filter"
        }
    ],
    
    "Indicators": [
        {
            "id": "moving_average",
            "name": "Moving Average",
            "description": "Calculate moving average of price",
            "inputs": ["price"],
            "outputs": ["ma_value"],
            "params": {
                "period": {
                    "type": "number",
                    "min": 1,
                    "max": 200,
                    "default": 20,
                    "description": "Period for calculating the moving average"
                },
                "ma_type": {
                    "type": "select",
                    "options": ["simple", "exponential", "weighted"],
                    "default": "simple",
                    "description": "Type of moving average calculation"
                }
            },
            "icon": "trending-up"
        },
        {
            "id": "rsi",
            "name": "RSI",
            "description": "Relative Strength Index",
            "inputs": ["price"],
            "outputs": ["rsi_value"],
            "params": {
                "period": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 14,
                    "description": "Period for calculating RSI"
                }
            },
            "icon": "activity"
        },
        {
            "id": "bollinger_bands",
            "name": "Bollinger Bands",
            "description": "Bollinger Bands indicator",
            "inputs": ["price"],
            "outputs": ["upper_band", "middle_band", "lower_band"],
            "params": {
                "period": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 20,
                    "description": "Period for calculating the middle band (SMA)"
                },
                "stdev": {
                    "type": "number",
                    "min": 0.5,
                    "max": 5,
                    "default": 2,
                    "description": "Number of standard deviations for the bands"
                }
            },
            "icon": "trending-up"
        },
        {
            "id": "macd",
            "name": "MACD",
            "description": "Moving Average Convergence Divergence",
            "inputs": ["price"],
            "outputs": ["macd_line", "signal_line", "histogram"],
            "params": {
                "fast": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 12,
                    "description": "Fast EMA period"
                },
                "slow": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 26,
                    "description": "Slow EMA period"
                },
                "signal": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 9,
                    "description": "Signal line period"
                }
            },
            "icon": "bar-chart-2"
        },
        {
            "id": "stochastic",
            "name": "Stochastic Oscillator",
            "description": "Stochastic Oscillator indicator",
            "inputs": ["high", "low", "close"],
            "outputs": ["%K", "%D"],
            "params": {
                "k_period": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 14,
                    "description": "Period for %K line"
                },
                "d_period": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 3,
                    "description": "Period for %D line (signal)"
                }
            },
            "icon": "activity"
        },
        {
            "id": "atr",
            "name": "ATR",
            "description": "Average True Range",
            "inputs": ["high", "low", "close"],
            "outputs": ["atr_value"],
            "params": {
                "period": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 14,
                    "description": "Period for calculating ATR"
                }
            },
            "icon": "bar-chart"
        },
        {
            "id": "volume_profile",
            "name": "Volume Profile",
            "description": "Volume distribution across price levels",
            "inputs": ["price", "volume"],
            "outputs": ["volume_by_price"],
            "params": {
                "bins": {
                    "type": "number",
                    "min": 5,
                    "max": 50,
                    "default": 20,
                    "description": "Number of price bins for volume distribution"
                }
            },
            "icon": "bar-chart"
        }
    ],
    
    "Entry Conditions": [
        {
            "id": "entry_condition",
            "name": "Entry Condition",
            "description": "Define when to enter a trade",
            "inputs": ["indicators"],
            "outputs": ["signal"],
            "params": {
                "condition": {
                    "type": "text",
                    "default": "SMA_20 > SMA_50",
                    "description": "Condition expression (e.g., SMA_20 > SMA_50)"
                },
                "direction": {
                    "type": "select",
                    "options": ["long", "short"],
                    "default": "long",
                    "description": "Trade direction"
                }
            },
            "icon": "log-in"
        },
        {
            "id": "ma_crossover",
            "name": "MA Crossover",
            "description": "Moving average crossover entry signal",
            "inputs": ["fast_ma", "slow_ma"],
            "outputs": ["signal"],
            "params": {
                "direction": {
                    "type": "select",
                    "options": ["bullish", "bearish"],
                    "default": "bullish",
                    "description": "Crossover direction (bullish: fast crosses above slow)"
                }
            },
            "icon": "trending-up"
        },
        {
            "id": "price_breakout",
            "name": "Price Breakout",
            "description": "Enter when price breaks above/below a level",
            "inputs": ["price", "level"],
            "outputs": ["signal"],
            "params": {
                "direction": {
                    "type": "select",
                    "options": ["above", "below"],
                    "default": "above",
                    "description": "Breakout direction"
                },
                "period": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 20,
                    "description": "Period for calculating the breakout level"
                }
            },
            "icon": "trending-up"
        },
        {
            "id": "rsi_signal",
            "name": "RSI Signal",
            "description": "Enter based on RSI crossing levels",
            "inputs": ["rsi"],
            "outputs": ["signal"],
            "params": {
                "level": {
                    "type": "number",
                    "min": 1,
                    "max": 99,
                    "default": 30,
                    "description": "RSI level to trigger entry"
                },
                "direction": {
                    "type": "select",
                    "options": ["above", "below"],
                    "default": "above",
                    "description": "Direction of RSI cross"
                }
            },
            "icon": "activity"
        }
    ],
    
    "Exit Conditions": [
        {
            "id": "exit_condition",
            "name": "Exit Condition",
            "description": "Define when to exit a trade",
            "inputs": ["indicators"],
            "outputs": ["signal"],
            "params": {
                "condition": {
                    "type": "text",
                    "default": "RSI_14 > 70",
                    "description": "Condition expression (e.g., RSI_14 > 70)"
                }
            },
            "icon": "log-out"
        },
        {
            "id": "trailing_stop",
            "name": "Trailing Stop",
            "description": "Exit using a trailing stop",
            "inputs": ["price", "atr"],
            "outputs": ["signal"],
            "params": {
                "multiplier": {
                    "type": "number",
                    "min": 0.5,
                    "max": 10,
                    "default": 2,
                    "description": "ATR multiplier for stop distance"
                }
            },
            "icon": "trending-down"
        },
        {
            "id": "time_exit",
            "name": "Time-Based Exit",
            "description": "Exit after a certain number of bars",
            "inputs": ["entry_time"],
            "outputs": ["signal"],
            "params": {
                "bars": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 10,
                    "description": "Number of bars to hold the position"
                }
            },
            "icon": "clock"
        },
        {
            "id": "profit_target",
            "name": "Profit Target",
            "description": "Exit when price reaches target profit level",
            "inputs": ["entry_price"],
            "outputs": ["signal"],
            "params": {
                "target_percent": {
                    "type": "number",
                    "min": 0.1,
                    "max": 100,
                    "default": 5,
                    "description": "Target profit percentage"
                }
            },
            "icon": "dollar-sign"
        }
    ],
    
    "Risk Management": [
        {
            "id": "stop_loss",
            "name": "Stop Loss",
            "description": "Set a stop loss level",
            "inputs": ["entry_price"],
            "outputs": ["stop_level"],
            "params": {
                "percent": {
                    "type": "number",
                    "min": 0.1,
                    "max": 20,
                    "default": 2,
                    "description": "Stop loss percentage"
                },
                "type": {
                    "type": "select",
                    "options": ["percent", "fixed", "atr_based"],
                    "default": "percent",
                    "description": "Stop loss calculation method"
                }
            },
            "icon": "trending-down"
        },
        {
            "id": "take_profit",
            "name": "Take Profit",
            "description": "Set a take profit level",
            "inputs": ["entry_price"],
            "outputs": ["profit_level"],
            "params": {
                "percent": {
                    "type": "number",
                    "min": 0.1,
                    "max": 50,
                    "default": 5,
                    "description": "Take profit percentage"
                },
                "type": {
                    "type": "select",
                    "options": ["percent", "fixed", "risk_reward"],
                    "default": "percent",
                    "description": "Take profit calculation method"
                }
            },
            "icon": "trending-up"
        },
        {
            "id": "position_sizing",
            "name": "Position Sizing",
            "description": "Calculate position size",
            "inputs": ["capital", "risk_per_trade"],
            "outputs": ["position_size"],
            "params": {
                "risk_percent": {
                    "type": "number",
                    "min": 0.1,
                    "max": 10,
                    "default": 1,
                    "description": "Risk percentage per trade"
                }
            },
            "icon": "percent"
        },
        {
            "id": "max_open_trades",
            "name": "Max Open Trades",
            "description": "Limit the number of open trades",
            "inputs": ["open_positions"],
            "outputs": ["can_trade"],
            "params": {
                "max_trades": {
                    "type": "number",
                    "min": 1,
                    "max": 20,
                    "default": 3,
                    "description": "Maximum number of open positions"
                }
            },
            "icon": "layers"
        },
        {
            "id": "risk_reward_filter",
            "name": "Risk-Reward Filter",
            "description": "Filter trades based on risk-reward ratio",
            "inputs": ["stop_level", "take_profit_level"],
            "outputs": ["trade_valid"],
            "params": {
                "min_ratio": {
                    "type": "number",
                    "min": 0.5,
                    "max": 10,
                    "default": 2,
                    "description": "Minimum risk-reward ratio"
                }
            },
            "icon": "sliders"
        }
    ],
    
    "Order Execution": [
        {
            "id": "market_order",
            "name": "Market Order",
            "description": "Execute a market order",
            "inputs": ["signal", "position_size"],
            "outputs": ["order"],
            "params": {
                "direction": {
                    "type": "select",
                    "options": ["buy", "sell"],
                    "default": "buy",
                    "description": "Order direction"
                }
            },
            "icon": "shopping-cart"
        },
        {
            "id": "limit_order",
            "name": "Limit Order",
            "description": "Execute a limit order",
            "inputs": ["signal", "position_size", "price"],
            "outputs": ["order"],
            "params": {
                "direction": {
                    "type": "select",
                    "options": ["buy", "sell"],
                    "default": "buy",
                    "description": "Order direction"
                },
                "offset": {
                    "type": "number",
                    "min": -10,
                    "max": 10,
                    "default": 0.5,
                    "description": "Price offset percentage"
                }
            },
            "icon": "shopping-bag"
        },
        {
            "id": "stop_order",
            "name": "Stop Order",
            "description": "Execute a stop order",
            "inputs": ["signal", "position_size", "price"],
            "outputs": ["order"],
            "params": {
                "direction": {
                    "type": "select",
                    "options": ["buy", "sell"],
                    "default": "buy",
                    "description": "Order direction"
                },
                "offset": {
                    "type": "number",
                    "min": -10,
                    "max": 10,
                    "default": 0.5,
                    "description": "Price offset percentage"
                }
            },
            "icon": "alert-circle"
        },
        {
            "id": "order_cancellation",
            "name": "Order Cancellation",
            "description": "Cancel an order after a specified time",
            "inputs": ["order"],
            "outputs": ["cancel_signal"],
            "params": {
                "timeout_bars": {
                    "type": "number",
                    "min": 1,
                    "max": 100,
                    "default": 5,
                    "description": "Number of bars after which to cancel the order"
                }
            },
            "icon": "x-circle"
        }
    ]
}

# Block Templates
BLOCK_TEMPLATES = {
    "moving_average_crossover_strategy": {
        "name": "Moving Average Crossover Strategy",
        "description": "A simple strategy that enters when a faster moving average crosses above a slower moving average and exits when it crosses below",
        "blocks": [
            {
                "id": "price_data_1",
                "type": "price_data",
                "position": {"x": 100, "y": 100}
            },
            {
                "id": "ma_fast",
                "type": "moving_average",
                "position": {"x": 300, "y": 50},
                "params": {
                    "period": 20,
                    "ma_type": "simple"
                }
            },
            {
                "id": "ma_slow",
                "type": "moving_average",
                "position": {"x": 300, "y": 150},
                "params": {
                    "period": 50,
                    "ma_type": "simple"
                }
            },
            {
                "id": "entry_condition_1",
                "type": "entry_condition",
                "position": {"x": 500, "y": 100},
                "params": {
                    "condition": "SMA_20 > SMA_50",
                    "direction": "long"
                }
            },
            {
                "id": "exit_condition_1",
                "type": "exit_condition",
                "position": {"x": 500, "y": 200},
                "params": {
                    "condition": "SMA_20 < SMA_50"
                }
            },
            {
                "id": "stop_loss_1",
                "type": "stop_loss",
                "position": {"x": 700, "y": 50},
                "params": {
                    "percent": 2,
                    "type": "percent"
                }
            },
            {
                "id": "take_profit_1",
                "type": "take_profit",
                "position": {"x": 700, "y": 150},
                "params": {
                    "percent": 6,
                    "type": "percent"
                }
            },
            {
                "id": "market_order_1",
                "type": "market_order",
                "position": {"x": 900, "y": 100},
                "params": {
                    "direction": "buy"
                }
            }
        ],
        "connections": [
            {
                "id": "conn_1",
                "source_id": "price_data_1",
                "target_id": "ma_fast",
                "output_name": "Close",
                "input_name": "price"
            },
            {
                "id": "conn_2",
                "source_id": "price_data_1",
                "target_id": "ma_slow",
                "output_name": "Close",
                "input_name": "price"
            },
            {
                "id": "conn_3",
                "source_id": "entry_condition_1",
                "target_id": "market_order_1",
                "output_name": "signal",
                "input_name": "signal"
            }
        ]
    },
    
    "rsi_oversold_strategy": {
        "name": "RSI Oversold Strategy",
        "description": "Enters when RSI is oversold (below 30) and exits when RSI moves above 70",
        "blocks": [
            {
                "id": "price_data_1",
                "type": "price_data",
                "position": {"x": 100, "y": 100}
            },
            {
                "id": "rsi_1",
                "type": "rsi",
                "position": {"x": 300, "y": 100},
                "params": {
                    "period": 14
                }
            },
            {
                "id": "entry_condition_1",
                "type": "entry_condition",
                "position": {"x": 500, "y": 50},
                "params": {
                    "condition": "RSI_14 < 30",
                    "direction": "long"
                }
            },
            {
                "id": "exit_condition_1",
                "type": "exit_condition",
                "position": {"x": 500, "y": 150},
                "params": {
                    "condition": "RSI_14 > 70"
                }
            },
            {
                "id": "stop_loss_1",
                "type": "stop_loss",
                "position": {"x": 700, "y": 50},
                "params": {
                    "percent": 2,
                    "type": "percent"
                }
            },
            {
                "id": "market_order_1",
                "type": "market_order",
                "position": {"x": 700, "y": 150},
                "params": {
                    "direction": "buy"
                }
            }
        ],
        "connections": [
            {
                "id": "conn_1",
                "source_id": "price_data_1",
                "target_id": "rsi_1",
                "output_name": "Close",
                "input_name": "price"
            },
            {
                "id": "conn_2",
                "source_id": "entry_condition_1",
                "target_id": "market_order_1",
                "output_name": "signal",
                "input_name": "signal"
            }
        ]
    },
    
    "bollinger_band_strategy": {
        "name": "Bollinger Band Reversion Strategy",
        "description": "Enters when price touches the lower Bollinger Band and RSI is below 30, exits when price reaches the middle band or upper band",
        "blocks": [
            {
                "id": "price_data_1",
                "type": "price_data",
                "position": {"x": 100, "y": 100}
            },
            {
                "id": "bollinger_1",
                "type": "bollinger_bands",
                "position": {"x": 300, "y": 50},
                "params": {
                    "period": 20,
                    "stdev": 2
                }
            },
            {
                "id": "rsi_1",
                "type": "rsi",
                "position": {"x": 300, "y": 150},
                "params": {
                    "period": 14
                }
            },
            {
                "id": "entry_condition_1",
                "type": "entry_condition",
                "position": {"x": 500, "y": 100},
                "params": {
                    "condition": "Close < BB_Lower_20 and RSI_14 < 30",
                    "direction": "long"
                }
            },
            {
                "id": "exit_condition_1",
                "type": "exit_condition",
                "position": {"x": 500, "y": 200},
                "params": {
                    "condition": "Close > BB_Middle_20"
                }
            },
            {
                "id": "stop_loss_1",
                "type": "stop_loss",
                "position": {"x": 700, "y": 50},
                "params": {
                    "percent": 1.5,
                    "type": "percent"
                }
            },
            {
                "id": "take_profit_1",
                "type": "take_profit",
                "position": {"x": 700, "y": 150},
                "params": {
                    "percent": 3,
                    "type": "percent"
                }
            },
            {
                "id": "market_order_1",
                "type": "market_order",
                "position": {"x": 900, "y": 100},
                "params": {
                    "direction": "buy"
                }
            }
        ],
        "connections": [
            {
                "id": "conn_1",
                "source_id": "price_data_1",
                "target_id": "bollinger_1",
                "output_name": "Close",
                "input_name": "price"
            },
            {
                "id": "conn_2",
                "source_id": "price_data_1",
                "target_id": "rsi_1",
                "output_name": "Close",
                "input_name": "price"
            },
            {
                "id": "conn_3",
                "source_id": "entry_condition_1",
                "target_id": "market_order_1",
                "output_name": "signal",
                "input_name": "signal"
            }
        ]
    }
}

# Block connection rules
CONNECTION_RULES = {
    "valid_connections": [
        # Data to indicators
        {"source_type": "price_data", "target_type": "moving_average"},
        {"source_type": "price_data", "target_type": "rsi"},
        {"source_type": "price_data", "target_type": "bollinger_bands"},
        {"source_type": "price_data", "target_type": "macd"},
        {"source_type": "price_data", "target_type": "stochastic"},
        
        # Indicators to entry/exit conditions
        {"source_type": "moving_average", "target_type": "entry_condition"},
        {"source_type": "moving_average", "target_type": "exit_condition"},
        {"source_type": "rsi", "target_type": "entry_condition"},
        {"source_type": "rsi", "target_type": "exit_condition"},
        {"source_type": "bollinger_bands", "target_type": "entry_condition"},
        {"source_type": "bollinger_bands", "target_type": "exit_condition"},
        {"source_type": "macd", "target_type": "entry_condition"},
        {"source_type": "macd", "target_type": "exit_condition"},
        
        # Conditions to orders
        {"source_type": "entry_condition", "target_type": "market_order"},
        {"source_type": "entry_condition", "target_type": "limit_order"},
        {"source_type": "exit_condition", "target_type": "market_order"},
        {"source_type": "exit_condition", "target_type": "limit_order"},
        
        # Risk management
        {"source_type": "entry_condition", "target_type": "stop_loss"},
        {"source_type": "entry_condition", "target_type": "take_profit"},
        {"source_type": "stop_loss", "target_type": "market_order"},
        {"source_type": "take_profit", "target_type": "market_order"}
    ]
}

# Helper functions
def get_block_categories():
    """
    Get the available block categories
    
    Returns:
    --------
    list
        List of block categories
    """
    return BLOCK_CATEGORIES

def get_blocks_by_category(category):
    """
    Get blocks available in a specific category
    
    Parameters:
    -----------
    category : str
        Block category
        
    Returns:
    --------
    list
        List of blocks in the category
    """
    return BLOCKS_BY_CATEGORY.get(category, [])

def get_block_templates():
    """
    Get available block templates
    
    Returns:
    --------
    dict
        Dictionary of block templates
    """
    return BLOCK_TEMPLATES

def get_connection_rules():
    """
    Get the rules for valid connections between blocks
    
    Returns:
    --------
    dict
        Dictionary of connection rules
    """
    return CONNECTION_RULES

def is_valid_connection(source_type, target_type):
    """
    Check if a connection between block types is valid
    
    Parameters:
    -----------
    source_type : str
        Source block type
    target_type : str
        Target block type
        
    Returns:
    --------
    bool
        True if connection is valid, False otherwise
    """
    rules = CONNECTION_RULES["valid_connections"]
    return any(rule["source_type"] == source_type and rule["target_type"] == target_type for rule in rules)
