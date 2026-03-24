# gui/streamlit_app.py
import streamlit as st
import pandas as pd
from source.lru_cache import LRUCacheSimulator
from source.mru_cache import MRUCacheSimulator
from source.test_cases import TestSequenceGenerator

def render_gui():
    st.set_page_config(page_title="Cache Simulator", layout="wide")
    st.title("🖥️ Fully Associative Cache Simulator")

    # --- 1. Configuration Section (Horizontal) ---
    st.subheader("Configuration")
    
    col_layout = [1, 1, 1, 1, 1]
    c1, c2, c3, c4, c5 = st.columns(col_layout)

    power_of_2_options = [2**i for i in range(11)]
    
    with c1:
        policy = st.selectbox("Replacement Policy", ["LRU", "MRU"])
    with c2:
        w_p_b = st.selectbox("Words/Block", options=power_of_2_options, index=2)
    with c3:
        n_b = st.selectbox("Cache Blocks", options=power_of_2_options, index=2)
    with c4:
        h_t = st.number_input("Hit Time (ns)", value=1, min_value=1)
    with c5:
        m_t = st.number_input("Miss Penalty (ns)", value=100, min_value=1)

    r2_c1, r2_c2, r2_c3, r2_c4, r2_c5 = st.columns(col_layout)
    
    with r2_c3:
        if st.button("Initialize / Reset Cache", use_container_width=True):
            # Save the parameters so we can precisely rebuild the cache when stepping backwards
            st.session_state.sim_params = {
                'policy': policy, 'w_p_b': w_p_b, 'n_b': n_b, 'h_t': h_t, 'm_t': m_t
            }
            
            if policy == "LRU":
                st.session_state.sim = LRUCacheSimulator(w_p_b, n_b, h_t, m_t)
            else:
                st.session_state.sim = MRUCacheSimulator(w_p_b, n_b, h_t, m_t)
            
            st.session_state.current_policy = policy
            st.session_state.test_gen = TestSequenceGenerator(n_b)
            st.session_state.step_index = 0
            st.toast(f"Initialized {policy} Cache", icon="✅")

    st.divider()

    if 'sim' not in st.session_state:
        st.info("Please initialize the cache above to begin.")
        return

    if 'step_index' not in st.session_state:
        st.session_state.step_index = 0

    # --- 2. Access Sequence ---
    st.subheader("Access Sequence")
    row1_col1, row1_col2 = st.columns([1, 3])

    with row1_col1:
        test_choice = st.selectbox(
            "Select Test Case", 
            ["Manual Input", "Sequential Sequence", "Mid-Repeat Blocks", "Random Sequence"]
        )

    with row1_col2:
        if test_choice == "Manual Input":
            addr_input = st.text_input("Enter Block IDs (comma separated)", "0, 1, 2, 3")
            try:
                current_parsed_seq = [int(x.strip()) for x in addr_input.split(",") if x.strip()]
            except ValueError:
                st.error("Invalid input. Please enter integers separated by commas.")
                current_parsed_seq = []
        else:
            if 'cached_test_choice' not in st.session_state or st.session_state.cached_test_choice != test_choice:
                gen = st.session_state.test_gen
                if test_choice == "Sequential Sequence":
                    st.session_state.cached_seq = gen.get_sequential()
                elif test_choice == "Mid-Repeat Blocks":
                    st.session_state.cached_seq = gen.get_mid_repeat()
                elif test_choice == "Random Sequence":
                    st.session_state.cached_seq = gen.get_random()
                st.session_state.cached_test_choice = test_choice
            
            current_parsed_seq = st.session_state.cached_seq
            st.code(f"{current_parsed_seq}", language="python")

    if 'last_sequence' not in st.session_state or st.session_state.last_sequence != current_parsed_seq:
        st.session_state.last_sequence = current_parsed_seq
        st.session_state.step_index = 0
    
    final_sequence = current_parsed_seq

    # --- 3. Simulation Controls ---
    st.subheader("Simulation Controls")
    
    if not final_sequence:
        st.warning("Sequence is empty!")
    else:
        # Created 4 columns to fit the new "Step Back" button
        b_c1, b_c2, b_c3, b_c4 = st.columns(4)
        
        with b_c1:
            if st.button("Step Back ⬅️", use_container_width=True):
                if st.session_state.step_index > 0:
                    st.session_state.step_index -= 1
                    
                    # Rebuild the simulator state from scratch up to the new step_index
                    p = st.session_state.sim_params
                    if p['policy'] == "LRU":
                        st.session_state.sim = LRUCacheSimulator(p['w_p_b'], p['n_b'], p['h_t'], p['m_t'])
                    else:
                        st.session_state.sim = MRUCacheSimulator(p['w_p_b'], p['n_b'], p['h_t'], p['m_t'])
                    
                    # Fast-forward simulation to the current step
                    for i in range(st.session_state.step_index):
                        st.session_state.sim.access(final_sequence[i])

        with b_c2:
            if st.button("Step Fwd ➡️", use_container_width=True):
                if st.session_state.step_index < len(final_sequence):
                    st.session_state.sim.access(final_sequence[st.session_state.step_index])
                    st.session_state.step_index += 1
                
        with b_c3:
            if st.button("Simulate Rest ⏩", use_container_width=True):
                while st.session_state.step_index < len(final_sequence):
                    st.session_state.sim.access(final_sequence[st.session_state.step_index])
                    st.session_state.step_index += 1
                st.toast("Simulation Complete!", icon="✅")
                
        with b_c4:
            if st.button("Restart Sequence 🔄", use_container_width=True):
                p = st.session_state.sim_params
                if p['policy'] == "LRU":
                    st.session_state.sim = LRUCacheSimulator(p['w_p_b'], p['n_b'], p['h_t'], p['m_t'])
                else:
                    st.session_state.sim = MRUCacheSimulator(p['w_p_b'], p['n_b'], p['h_t'], p['m_t'])
                st.session_state.step_index = 0
                st.toast("Sequence restarted and cache cleared.", icon="🔄")

        # Progress Indicator
        progress_val = st.session_state.step_index / len(final_sequence) if final_sequence else 0
        st.progress(progress_val)
        
        if st.session_state.step_index < len(final_sequence):
            st.markdown(f"**Step {st.session_state.step_index} / {len(final_sequence)}** | **Next Block ID:** `{final_sequence[st.session_state.step_index]}`")
        else:
            st.markdown(f"**Step {st.session_state.step_index} / {len(final_sequence)}** | 🎉 **All instructions processed!**")

    st.divider()

    # --- 4. Snapshots and Logs ---
    col_snap, col_log = st.columns([1, 1])
    
    with col_snap:
        st.subheader("Cache Memory Snapshot")
        if st.session_state.sim.cache:
            df_cache = pd.DataFrame(st.session_state.sim.cache)
            st.dataframe(df_cache, hide_index=True) 
        else:
            st.info("Cache is empty.")

    with col_log:
        st.subheader("Trace Log")
        if hasattr(st.session_state.sim, 'trace_log'):
            st.text_area("Activity Log", value="\n".join(st.session_state.sim.trace_log), height=300)
        else:
            st.text_area("Activity Log", value="", height=300)

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

    st.subheader("Performance Metrics")
    
    metrics = st.session_state.sim.calculate_metrics()

    def metric_bubble(label, value):
        st.markdown(f"""
            <div class="metric-bubble">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        metric_bubble("Memory Access Count", metrics.get("Access Count", 0))
    with m_col2:
        metric_bubble("Cache Hit Count", metrics.get("Hits", 0))
    with m_col3:
        metric_bubble("Cache Miss Count", metrics.get("Misses", 0))

    m_col4, m_col5, m_col6, m_col7 = st.columns(4)
    with m_col4:
        metric_bubble("Hit Rate", metrics.get("Hit Rate", "0%"))
    with m_col5:
        metric_bubble("Miss Rate", metrics.get("Miss Rate", "0%"))
    with m_col6:
        metric_bubble("Avg Access Time", metrics.get("AMAT", "0 ns"))
    with m_col7:
        metric_bubble("Total Access Time", metrics.get("Total Time", "0 ns"))