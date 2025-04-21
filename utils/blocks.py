"""
Module for handling block operations in the AlgoBlocks system
"""

def get_block_categories():
    """
    Get the available block categories
    
    Returns:
    --------
    list
        List of block categories
    """
    return [
        "Data Inputs",
        "Indicators",
        "Entry Conditions",
        "Exit Conditions",
        "Risk Management",
        "Order Execution"
    ]

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
    blocks_by_category = {
        "Data Inputs": [
            {
                "id": "price_data",
                "name": "Price Data",
                "description": "OHLCV price data from the selected ticker",
                "inputs": [],
                "outputs": ["Open", "High", "Low", "Close", "Volume"]
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
                }
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
                        "default": 20
                    },
                    "ma_type": {
                        "type": "select",
                        "options": ["simple", "exponential", "weighted"],
                        "default": "simple"
                    }
                }
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
                        "default": 14
                    }
                }
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
                        "default": 20
                    },
                    "stdev": {
                        "type": "number",
                        "min": 0.5,
                        "max": 5,
                        "default": 2
                    }
                }
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
                        "default": 12
                    },
                    "slow": {
                        "type": "number",
                        "min": 1,
                        "max": 100,
                        "default": 26
                    },
                    "signal": {
                        "type": "number",
                        "min": 1,
                        "max": 100,
                        "default": 9
                    }
                }
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
                        "default": 14
                    },
                    "d_period": {
                        "type": "number",
                        "min": 1,
                        "max": 100,
                        "default": 3
                    }
                }
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
                        "default": "SMA_20 > SMA_50"
                    },
                    "direction": {
                        "type": "select",
                        "options": ["long", "short"],
                        "default": "long"
                    }
                }
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
                        "default": "bullish"
                    }
                }
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
                        "default": "RSI_14 > 70"
                    }
                }
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
                        "default": 2
                    }
                }
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
                        "default": 2
                    },
                    "type": {
                        "type": "select",
                        "options": ["percent", "fixed", "atr_based"],
                        "default": "percent"
                    }
                }
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
                        "default": 5
                    },
                    "type": {
                        "type": "select",
                        "options": ["percent", "fixed", "risk_reward"],
                        "default": "percent"
                    }
                }
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
                        "default": 1
                    }
                }
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
                        "default": "buy"
                    }
                }
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
                        "default": "buy"
                    },
                    "offset": {
                        "type": "number",
                        "min": -10,
                        "max": 10,
                        "default": 0.5
                    }
                }
            }
        ]
    }
    
    return blocks_by_category.get(category, [])

def create_block(block_type, block_id=None, params=None):
    """
    Create a new block of the specified type
    
    Parameters:
    -----------
    block_type : str
        Type of block to create
    block_id : str, optional
        Custom ID for the block
    params : dict, optional
        Parameters for the block
        
    Returns:
    --------
    dict
        Block configuration
    """
    # Find the block template from all categories
    block_template = None
    for category in get_block_categories():
        blocks = get_blocks_by_category(category)
        for block in blocks:
            if block['id'] == block_type:
                block_template = block
                break
        if block_template:
            break
    
    if not block_template:
        return None
    
    # Create a new block based on the template
    import uuid
    block_id = block_id or str(uuid.uuid4())
    
    block = {
        'id': block_id,
        'type': block_type,
        'name': block_template['name'],
        'inputs': block_template.get('inputs', []),
        'outputs': block_template.get('outputs', []),
        'params': params or {}
    }
    
    # Set default parameters if not provided
    if 'params' in block_template:
        for param_name, param_config in block_template['params'].items():
            if param_name not in block['params']:
                block['params'][param_name] = param_config.get('default')
    
    return block

def validate_connection(source_block, target_block, output_name, input_name):
    """
    Validate if a connection between blocks is valid
    
    Parameters:
    -----------
    source_block : dict
        Source block configuration
    target_block : dict
        Target block configuration
    output_name : str
        Output name from source block
    input_name : str
        Input name to target block
        
    Returns:
    --------
    bool
        True if connection is valid, False otherwise
    """
    # Check if output exists in source block
    if output_name not in source_block.get('outputs', []):
        return False
    
    # Check if input exists in target block
    if input_name not in target_block.get('inputs', []):
        return False
    
    # TODO: Add more sophisticated validation based on data types
    
    return True

def create_connection(source_id, target_id, output_name, input_name):
    """
    Create a connection between two blocks
    
    Parameters:
    -----------
    source_id : str
        ID of the source block
    target_id : str
        ID of the target block
    output_name : str
        Output name from source block
    input_name : str
        Input name to target block
        
    Returns:
    --------
    dict
        Connection configuration
    """
    import uuid
    connection_id = str(uuid.uuid4())
    
    return {
        'id': connection_id,
        'source_id': source_id,
        'target_id': target_id,
        'output_name': output_name,
        'input_name': input_name
    }
