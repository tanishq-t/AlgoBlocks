import streamlit as st
import json
import pandas as pd
import numpy as np
from components.block_canvas import display_block_canvas
from utils.strategy import execute_strategy

def display_strategy_builder():
    """
    Display the strategy builder page
    """
    st.header("Strategy Builder")
    st.write("Create your algorithmic trading strategy using blocks")
    
    # Strategy name and description
    col1, col2 = st.columns(2)
    with col1:
        strategy_name = st.text_input("Strategy Name", "My Trading Strategy")
    with col2:
        strategy_description = st.text_input("Description", "A simple algorithmic trading strategy")
    
    # Block canvas for building the strategy
    display_block_canvas()
    
    # Strategy Summary
    st.markdown("---")
    st.subheader("Strategy Summary")
    
    if 'strategy' in st.session_state and st.session_state.strategy.get('blocks'):
        st.write(f"**Blocks:** {len(st.session_state.strategy['blocks'])}")
        st.write(f"**Connections:** {len(st.session_state.strategy['connections'])}")
        
        # Display block types used
        block_types = {}
        for block in st.session_state.strategy['blocks']:
            block_type = block['type']
            if block_type in block_types:
                block_types[block_type] += 1
            else:
                block_types[block_type] = 1
        
        st.write("**Block Types:**")
        for block_type, count in block_types.items():
            st.write(f"- {block_type}: {count}")
            
        # Allow strategy export/import
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Export strategy
            if st.button("Export Strategy"):
                strategy_json = json.dumps({
                    'name': strategy_name,
                    'description': strategy_description,
                    'blocks': st.session_state.strategy['blocks'],
                    'connections': st.session_state.strategy['connections']
                }, indent=2)
                
                st.download_button(
                    label="Download Strategy JSON",
                    data=strategy_json,
                    file_name=f"{strategy_name.replace(' ', '_')}.json",
                    mime="application/json"
                )
        
        with col2:
            # Import strategy
            uploaded_file = st.file_uploader("Import Strategy", type="json")
            if uploaded_file is not None:
                try:
                    import_data = json.load(uploaded_file)
                    if 'blocks' in import_data and 'connections' in import_data:
                        # Update session state with imported strategy
                        st.session_state.strategy = {
                            'blocks': import_data['blocks'],
                            'connections': import_data['connections']
                        }
                        st.session_state.canvas_blocks = import_data['blocks']
                        st.session_state.canvas_connections = import_data['connections']
                        
                        # Update name and description if present
                        if 'name' in import_data:
                            strategy_name = import_data['name']
                        if 'description' in import_data:
                            strategy_description = import_data['description']
                            
                        st.success("Strategy imported successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid strategy file format")
                except Exception as e:
                    st.error(f"Error importing strategy: {e}")
        
        # Strategy validation
        st.markdown("---")
        st.subheader("Strategy Validation")
        
        if st.button("Validate Strategy"):
            # Check if we have ticker data
            if 'ticker_data' not in st.session_state or st.session_state.ticker_data is None:
                st.warning("Please load ticker data first from the Data Viewer tab")
            else:
                # Basic validation checks
                validation_errors = []
                
                # Check for blocks
                if not st.session_state.strategy.get('blocks'):
                    validation_errors.append("Strategy has no blocks")
                
                # Check for connections
                if not st.session_state.strategy.get('connections'):
                    validation_errors.append("Strategy has no connections between blocks")
                
                # Check for entry conditions
                has_entry = any(b['type'] == 'entry_condition' for b in st.session_state.strategy.get('blocks', []))
                if not has_entry:
                    validation_errors.append("Strategy has no entry conditions")
                
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    # Run basic strategy execution to check for runtime errors
                    try:
                        # Use a sample of the data for validation
                        sample_data = st.session_state.ticker_data.copy()
                        if len(sample_data) > 100:
                            sample_data = sample_data.iloc[-100:]
                        
                        result = execute_strategy(sample_data, st.session_state.strategy)
                        
                        # Check if signals were generated
                        signal_count = (result['signal'] != 0).sum()
                        
                        if signal_count > 0:
                            st.success(f"Strategy validated successfully! Generated {signal_count} signals on the test data.")
                        else:
                            st.warning("Strategy validated but did not generate any signals on the test data.")
                    
                    except Exception as e:
                        st.error(f"Error during strategy execution: {e}")
    else:
        st.info("No strategy has been created yet. Use the block canvas above to build your strategy.")
