import streamlit as st
import json
from utils.blocks import get_block_categories, get_blocks_by_category, create_block, create_connection, validate_connection

def display_block_canvas():
    """
    Display the block canvas for creating trading strategies
    """
    st.markdown("## Block Canvas")
    st.info("Drag and drop blocks to create your trading strategy")
    
    # Get blocks from session state or initialize
    if 'canvas_blocks' not in st.session_state:
        st.session_state.canvas_blocks = []
    if 'canvas_connections' not in st.session_state:
        st.session_state.canvas_connections = []
    
    # Simple canvas representation (to be replaced with a more interactive component in a real app)
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### Block Library")
        
        # Block categories accordion
        for category in get_block_categories():
            with st.expander(category):
                blocks = get_blocks_by_category(category)
                for block in blocks:
                    if st.button(f"{block['name']}", key=f"add_{block['id']}"):
                        # Create a new block and add to canvas
                        new_block = create_block(block['id'])
                        if new_block:
                            # Position the block (simplified)
                            new_block['position'] = {'x': 100, 'y': 100 * (len(st.session_state.canvas_blocks) + 1)}
                            st.session_state.canvas_blocks.append(new_block)
                            st.rerun()
    
    with col2:
        st.markdown("### Canvas")
        
        # Display blocks on canvas
        if not st.session_state.canvas_blocks:
            st.info("Add blocks from the library to start building your strategy")
        else:
            # Display blocks and their connections
            for i, block in enumerate(st.session_state.canvas_blocks):
                with st.container():
                    # Show block UI
                    with st.expander(f"{block['name']} ({block['type']})", expanded=True):
                        # Edit block parameters
                        updated_params = {}
                        for param_name, param_value in block['params'].items():
                            if isinstance(param_value, (int, float)):
                                updated_params[param_name] = st.number_input(
                                    f"{param_name}", 
                                    value=param_value,
                                    key=f"{block['id']}_{param_name}"
                                )
                            elif isinstance(param_value, str):
                                if param_name == 'condition':
                                    updated_params[param_name] = st.text_input(
                                        f"{param_name}", 
                                        value=param_value,
                                        key=f"{block['id']}_{param_name}"
                                    )
                                else:
                                    options = []
                                    # Try to determine options based on block type
                                    blocks_in_category = []
                                    for cat in get_block_categories():
                                        blocks_in_category.extend(get_blocks_by_category(cat))
                                    
                                    for b in blocks_in_category:
                                        if b['id'] == block['type'] and 'params' in b:
                                            if param_name in b['params'] and 'options' in b['params'][param_name]:
                                                options = b['params'][param_name]['options']
                                    
                                    if options:
                                        updated_params[param_name] = st.selectbox(
                                            f"{param_name}", 
                                            options=options,
                                            index=options.index(param_value) if param_value in options else 0,
                                            key=f"{block['id']}_{param_name}"
                                        )
                                    else:
                                        updated_params[param_name] = st.text_input(
                                            f"{param_name}", 
                                            value=param_value,
                                            key=f"{block['id']}_{param_name}"
                                        )
                        
                        # Update block parameters
                        st.session_state.canvas_blocks[i]['params'] = updated_params
                        
                        # Show block inputs and outputs
                        st.markdown("**Inputs:**")
                        if block['inputs']:
                            st.write(", ".join(block['inputs']))
                        else:
                            st.write("None")
                        
                        st.markdown("**Outputs:**")
                        if block['outputs']:
                            st.write(", ".join(block['outputs']))
                        else:
                            st.write("None")
                        
                        # Block Actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Delete Block", key=f"delete_{block['id']}"):
                                # Remove block and its connections
                                st.session_state.canvas_connections = [
                                    conn for conn in st.session_state.canvas_connections 
                                    if conn['source_id'] != block['id'] and conn['target_id'] != block['id']
                                ]
                                st.session_state.canvas_blocks.remove(block)
                                st.rerun()
            
            # Connection management
            st.markdown("### Connections")
            if len(st.session_state.canvas_blocks) > 1:
                with st.form("create_connection"):
                    st.subheader("Create Connection")
                    
                    # Create block selection options
                    block_options = {b['id']: f"{b['name']} ({b['type']})" for b in st.session_state.canvas_blocks}
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        source_id = st.selectbox("Source Block", options=list(block_options.keys()), 
                                                format_func=lambda x: block_options[x], key="source_block")
                        
                        # Get the source block
                        source_block = next((b for b in st.session_state.canvas_blocks if b['id'] == source_id), None)
                        
                        if source_block and source_block['outputs']:
                            output_name = st.selectbox("Output", options=source_block['outputs'], key="output_name")
                        else:
                            output_name = None
                            st.warning("Selected block has no outputs")
                    
                    with col2:
                        target_id = st.selectbox("Target Block", options=list(block_options.keys()), 
                                                format_func=lambda x: block_options[x], key="target_block")
                        
                        # Get the target block
                        target_block = next((b for b in st.session_state.canvas_blocks if b['id'] == target_id), None)
                        
                        if target_block and target_block['inputs']:
                            input_name = st.selectbox("Input", options=target_block['inputs'], key="input_name")
                        else:
                            input_name = None
                            st.warning("Selected block has no inputs")
                    
                    # Check if connection is valid
                    can_connect = False
                    if source_block and target_block and output_name and input_name:
                        can_connect = validate_connection(source_block, target_block, output_name, input_name)
                    
                    # Submit button
                    submit_button = st.form_submit_button("Create Connection")
                    
                    if submit_button:
                        if source_id == target_id:
                            st.error("Cannot connect a block to itself")
                        elif can_connect:
                            # Create connection
                            new_connection = create_connection(source_id, target_id, output_name, input_name)
                            st.session_state.canvas_connections.append(new_connection)
                            st.success("Connection created successfully")
                            st.rerun()
                        else:
                            st.error("Invalid connection. Please check source and target compatibility.")
            
            # Display existing connections
            if st.session_state.canvas_connections:
                st.subheader("Existing Connections")
                for i, conn in enumerate(st.session_state.canvas_connections):
                    source_block = next((b for b in st.session_state.canvas_blocks if b['id'] == conn['source_id']), {})
                    target_block = next((b for b in st.session_state.canvas_blocks if b['id'] == conn['target_id']), {})
                    
                    source_name = source_block.get('name', 'Unknown')
                    target_name = target_block.get('name', 'Unknown')
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"{source_name}.{conn['output_name']} → {target_name}.{conn['input_name']}")
                    with col3:
                        if st.button("Delete", key=f"del_conn_{i}"):
                            st.session_state.canvas_connections.remove(conn)
                            st.rerun()
    
    # Save strategy
    st.markdown("---")
    if st.button("Save Strategy"):
        if not st.session_state.canvas_blocks:
            st.warning("Strategy is empty. Add some blocks first.")
        else:
            # Save the current blocks and connections to the strategy
            st.session_state.strategy = {
                'blocks': st.session_state.canvas_blocks,
                'connections': st.session_state.canvas_connections
            }
            st.success("Strategy saved successfully!")
