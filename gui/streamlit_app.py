# gui/streamlit_app.py
import streamlit as st
from source.lru_cache import LRUCacheSimulator
from source.mru_cache import MRUCacheSimulator
from source.test_cases import TestSequenceGenerator

def render_gui():
    st.set_page_config(page_title="Cache Simulator", layout="wide")
    st.title("🖥️ Fully Associative Cache Simulator")

    # --- 1. Configuration Section (Horizontal) ---
    st.subheader("Configuration")
    
    # Create 5 columns for parameters and the reset button
    col_layout = [1, 1, 1, 1, 1]
    
    # First Row: Numeric Inputs
    c1, c2, c3, c4, c5 = st.columns(col_layout)

    power_of_2_options = [2**i for i in range(11)]
    
    with c1:
        policy = st.selectbox("Replacement Policy", ["LRU", "MRU"])
    with c2:
        # Use selectbox to ensure only power-of-2 values are chosen
        w_p_b = st.selectbox("Words/Block", options=power_of_2_options, index=2) # Default to 4
    with c3:
        # Use selectbox for Cache Blocks as well
        n_b = st.selectbox("Cache Blocks", options=power_of_2_options, index=2) # Default to 4
    with c4:
        h_t = st.number_input("Hit Time (ns)", value=1, min_value=1)
    with c5:
        m_t = st.number_input("Miss Penalty (ns)", value=100, min_value=1)

    # Center the Reset button slightly
    r2_c1, r2_c2, r2_c3, r2_c4, r2_c5 = st.columns(col_layout)
    
    with r2_c3:
        if st.button("Initialize / Reset Cache", use_container_width=True):
            if policy == "LRU":
                st.session_state.sim = LRUCacheSimulator(w_p_b, n_b, h_t, m_t)
            else:
                st.session_state.sim = MRUCacheSimulator(w_p_b, n_b, h_t, m_t)
            
            st.session_state.current_policy = policy
            st.session_state.test_gen = TestSequenceGenerator(n_b)
            st.toast(f"Initialized {policy} Cache", icon="✅")

    st.divider()

    st.divider()

    if 'sim' not in st.session_state:
        st.info("Please initialize the cache above to begin.")
        return

    # --- 2. Access Sequence (25/75 Split on One Row) ---
    st.subheader("Access Sequence")

    # This creates one row: Col1 (25%) | Col2 (75%)
    row1_col1, row1_col2 = st.columns([1, 3])

    with row1_col1:
        test_choice = st.selectbox(
            "Select Test Case", 
            ["Manual Input", "Sequential (2n repeated)", "Mid-Repeat Blocks", "Random (0 to 2n)"]
        )

    # Prepare sequence logic before rendering Col2
    final_sequence = []
    if test_choice != "Manual Input":
        gen = st.session_state.test_gen
        if test_choice == "Sequential Sequence":
            final_sequence = gen.get_sequential()
        elif test_choice == "Mid-Repeat Blocks":
            final_sequence = gen.get_mid_repeat()
        elif test_choice == "Random Sequence":
            final_sequence = gen.get_random()

    with row1_col2:
        if test_choice == "Manual Input":
            addr_input = st.text_input("Enter Block IDs (comma separated)", "0, 1, 2, 3")
            if addr_input:
                final_sequence = [int(x.strip()) for x in addr_input.split(",") if x.strip()]
        else:
            st.code(f"{final_sequence}", language="python")

    # --- 3. Simulation Button (Centered Below) ---
    b_c1, b_c2, b_c3 = st.columns([2, 1, 2])
    with b_c2:
        if st.button("🚀 Run Simulation", use_container_width=True):
            if not final_sequence:
                st.error("Sequence is empty!")
            else:
                st.session_state.sim.trace_log = []
                for a in final_sequence:
                    st.session_state.sim.access(a)
                st.success("Simulation Complete")

    st.divider()

   # --- Updated CSS for Bubble Metrics ---
    st.markdown("""
        <style>
            .metric-bubble {
                background-color: #f0f2f6;
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 15px;
                text-align: center;
                margin-bottom: 10px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
            }
            .metric-label {
                font-size: 0.9rem;
                color: #5f6368;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .metric-value {
                font-size: 1.4rem;
                color: #0e1117;
                font-weight: 800;
            }
        </style>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Performance Metrics")
    
    metrics = st.session_state.sim.calculate_metrics()

    # Helper function to render a bubble
    def metric_bubble(label, value):
        st.markdown(f"""
            <div class="metric-bubble">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)

    # Top Row: 3 Metrics (Access, Hits, Misses)
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        metric_bubble("Memory Access Count", metrics["Access Count"])
    with m_col2:
        metric_bubble("Cache Hit Count", metrics["Hits"])
    with m_col3:
        metric_bubble("Cache Miss Count", metrics["Misses"])

    # Bottom Row: 4 Metrics (Hit Rate, Miss Rate, AMAT, TMAT)
    m_col4, m_col5, m_col6, m_col7 = st.columns(4)
    with m_col4:
        metric_bubble("Hit Rate", metrics["Hit Rate"])
    with m_col5:
        metric_bubble("Miss Rate", metrics["Miss Rate"])
    with m_col6:
        metric_bubble("Avg Access Time", metrics["AMAT"])
    with m_col7:
        metric_bubble("Total Access Time", metrics["Total Time"])

    st.divider()

    # --- 4. Snapshots and Logs ---
    col_snap, col_log = st.columns([1, 1])
    
    with col_snap:
        st.subheader("a. Cache Memory Snapshot")
        if st.session_state.sim.cache:
            st.table(st.session_state.sim.cache)
        else:
            st.info("Cache is empty.")

    with col_log:
        st.subheader("a.ii Trace Log")
        st.text_area("Activity Log", value="\n".join(st.session_state.sim.trace_log), height=300)