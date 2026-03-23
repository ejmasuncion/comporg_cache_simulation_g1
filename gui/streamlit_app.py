# gui/streamlit_app.py
import streamlit as st
from source.lru_cache import LRUCacheSimulator
from source.mru_cache import MRUCacheSimulator

def render_gui():
    st.set_page_config(page_title="Cache Simulator", layout="wide")
    st.title("🖥️ Fully Associative Cache Simulator")

    # Sidebar for Parameters
    with st.sidebar:
        st.header("1. Configuration")
        
        # Policy Dropdown
        policy = st.selectbox("Replacement Policy", ["LRU", "MRU"])
        
        st.divider()
        
        w_p_b = st.number_input("Words per Block (Power of 2)", value=4, step=1)
        n_b = st.number_input("Cache Blocks (Power of 2)", value=4, step=1)
        h_t = st.number_input("Hit Time (ns)", value=1)
        m_t = st.number_input("Miss Penalty (ns)", value=100)
        
        if st.button("Reset / Initialize Cache"):
            # Determine which class to use based on dropdown selection
            if policy == "LRU":
                st.session_state.sim = LRUCacheSimulator(w_p_b, n_b, h_t, m_t)
            else:
                st.session_state.sim = MRUCacheSimulator(w_p_b, n_b, h_t, m_t)
            
            st.session_state.current_policy = policy
            st.success(f"Initialized with {policy}")

    # Check if simulation is initialized
    if 'sim' not in st.session_state:
        st.info("👈 Adjust parameters and click 'Reset / Initialize Cache' to start.")
        return

    # Display which policy is currently active
    st.subheader(f"Current Policy: {st.session_state.current_policy}")

    # Main Input
    addr_input = st.text_input("Enter Memory Addresses (comma separated)", "0, 4, 8, 0, 12, 4, 16")
    
    if st.button("Simulate All"):
        try:
            # Parse input and run simulation
            addrs = [int(x.strip()) for x in addr_input.split(",") if x.strip()]
            for a in addrs:
                st.session_state.sim.access(a)
            st.success("Simulation Processed!")
        except ValueError:
            st.error("Please enter valid integers separated by commas.")

    # Layout: Snapshot and Metrics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("a. Cache Memory Snapshot")
        if st.session_state.sim.cache:
            st.table(st.session_state.sim.cache)
        else:
            st.write("Cache is empty.")
        
        st.subheader("a.ii Text Log")
        log_text = "\n".join(st.session_state.sim.trace_log)
        st.text_area("Trace Log", value=log_text, height=300)

    with col2:
        st.subheader("b. Performance Metrics")
        metrics = st.session_state.sim.calculate_metrics()
        
        # Display each metric as a Streamlit metric card
        for k, v in metrics.items():
            st.metric(label=k, value=v)

    # Optional: Clear log button
    if st.button("Clear Trace Log"):
        st.session_state.sim.trace_log = []
        st.rerun()