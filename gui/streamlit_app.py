# gui/streamlit_app.py
import streamlit as st
from source.lru_cache import LRUCacheSimulator
from source.mru_cache import MRUCacheSimulator
from source.test_cases import TestSequenceGenerator

def render_gui():
    st.set_page_config(page_title="Cache Simulator", layout="wide")
    st.title("🖥️ Fully Associative Cache Simulator")

    # Sidebar for Parameters
    with st.sidebar:
        st.header("1. Configuration")
        policy = st.selectbox("Replacement Policy", ["LRU", "MRU"])
        
        st.divider()
        w_p_b = st.number_input("Words per Block (Power of 2)", value=4, step=1)
        n_b = st.number_input("Cache Blocks (Power of 2)", value=4, step=1)
        h_t = st.number_input("Hit Time (ns)", value=1)
        m_t = st.number_input("Miss Penalty (ns)", value=100)
        
        if st.button("Reset / Initialize Cache"):
            if policy == "LRU":
                st.session_state.sim = LRUCacheSimulator(w_p_b, n_b, h_t, m_t)
            else:
                st.session_state.sim = MRUCacheSimulator(w_p_b, n_b, h_t, m_t)
            
            st.session_state.current_policy = policy
            st.session_state.test_gen = TestSequenceGenerator(n_b, w_p_b)
            st.success(f"Initialized {policy} Cache")

    if 'sim' not in st.session_state:
        st.info("👈 Initialize the cache to begin.")
        return

    # 2. Test Case Selection
    st.subheader("2. Select Access Sequence")
    test_choice = st.selectbox(
        "Choose a Test Case or Manual Input", 
        ["Manual Input", "Sequential (2n repeated)", "Mid-Repeat Blocks", "Random (64 Blocks)"]
    )

    final_sequence = []

    if test_choice == "Manual Input":
        addr_input = st.text_input("Enter Word Addresses (comma separated)", "0, 1, 2")
        if addr_input:
            final_sequence = [int(x.strip()) for x in addr_input.split(",") if x.strip()]
    else:
        # Generate sequence using our new class
        gen = st.session_state.test_gen
        if test_choice == "Sequential (2n repeated)":
            final_sequence = gen.get_sequential()
        elif test_choice == "Mid-Repeat Blocks":
            final_sequence = gen.get_mid_repeat()
        elif test_choice == "Random (64 Blocks)":
            final_sequence = gen.get_random()
        
        st.code(f"Generated Sequence: {final_sequence}")

    if st.button("🚀 Run Simulation"):
        if not final_sequence:
            st.error("Sequence is empty!")
        else:
            # Clear previous logs if running a new test
            st.session_state.sim.trace_log = []
            for a in final_sequence:
                st.session_state.sim.access(a)
            st.success("Simulation Complete")

    # Layout: Snapshot and Metrics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("a. Cache Memory Snapshot")
        st.table(st.session_state.sim.cache)
        
        st.subheader("a.ii Trace Log")
        st.text_area("Log", value="\n".join(st.session_state.sim.trace_log), height=300)

    with col2:
        st.subheader("b. Performance Metrics")
        metrics = st.session_state.sim.calculate_metrics()
        for k, v in metrics.items():
            st.metric(label=k, value=v)