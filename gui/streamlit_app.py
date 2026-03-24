# gui/streamlit_app.py
import streamlit as st

# ADJUST COMMENTS TO 
# SWAP BETWEEN MRU AND LRU

# from source.mru_cache import FACacheSimulator
from source.mru_cache import FACacheSimulator


def render_gui():
    st.set_page_config(page_title="FA+LRU Cache Sim", layout="wide")
    st.title("🖥️ Cache Simulator (FA + LRU)")

    # Sidebar for Parameters
    with st.sidebar:
        st.header("1. Parameters")
        w_p_b = st.number_input("Words per Block (Power of 2)", value=4, step=1)
        n_b = st.number_input("Cache Blocks (Power of 2)", value=4, step=1)
        h_t = st.number_input("Hit Time (ns)", value=1)
        m_t = st.number_input("Miss Penalty (ns)", value=100)
        
        if st.button("Reset Cache"):
            st.session_state.sim = FACacheSimulator(w_p_b, n_b, h_t, m_t)
            st.session_state.history = []

    if 'sim' not in st.session_state:
        st.info("Adjust parameters and click 'Reset Cache' to start.")
        return

    # Main Input
    addr_input = st.text_input("Enter Memory Addresses (comma separated)", "0, 4, 8, 0, 12")
    
    if st.button("Simulate All"):
        addrs = [int(x.strip()) for x in addr_input.split(",")]
        for a in addrs:
            st.session_state.sim.access(a)
        st.success("Simulation Complete!")

    # Layout: Snapshot and Metrics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Cache Snapshot")
        st.table(st.session_state.sim.cache)
        
        st.subheader("Trace Log")
        st.text_area("Log", "\n".join(st.session_state.sim.trace_log), height=200)

    with col2:
        st.subheader("Performance")
        output = st.session_state.sim.miss_count
        metrics = st.session_state.sim.calculate_metrics()

        for k, v in metrics.items():
            st.metric(k, v)