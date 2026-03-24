import streamlit as st
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
            st.session_state.step_index = 0  # Reset the step counter

    # Initialize Session State
    if 'sim' not in st.session_state:
        st.session_state.sim = FACacheSimulator(w_p_b, n_b, h_t, m_t)
        st.session_state.history = []
        st.session_state.step_index = 0
        st.info("Adjust parameters and click 'Reset Cache' to start.")

    # Main Input
    addr_input = st.text_input("Enter Memory Addresses (comma separated)", "0, 4, 8, 0, 12")
    
    # Safely parse the input string into a list of integers
    try:
        addrs = [int(x.strip()) for x in addr_input.split(",") if x.strip() != ""]
    except ValueError:
        st.error("Please ensure all inputs are valid integers separated by commas.")
        addrs = []


    # Reset the step index if the user modifies the input string
    if 'last_input' not in st.session_state or st.session_state.last_input != addr_input:
        st.session_state.last_input = addr_input
        st.session_state.step_index = 0

    # Simulation Controls
    st.subheader("Simulation Controls")
    col_btn1, col_btn2 = st.columns([1, 1])
    
    with col_btn1:
        if st.button("Step ➡️", use_container_width=True):
            if st.session_state.step_index < len(addrs):
                current_addr = addrs[st.session_state.step_index]
                st.session_state.sim.access(current_addr)
                st.session_state.step_index += 1
            else:
                st.warning("End of instruction sequence reached. Modify the input or click 'Reset Cache'.")

    with col_btn2:
        if st.button("Simulate All ⏩", use_container_width=True):
            # Simulate whatever is left in the sequence
            while st.session_state.step_index < len(addrs):
                current_addr = addrs[st.session_state.step_index]
                st.session_state.sim.access(current_addr)
                st.session_state.step_index += 1
            st.success("Simulation Complete!")

    # Display progress
    if addrs:
        progress_val = st.session_state.step_index / len(addrs)
        st.progress(progress_val)
        
        if st.session_state.step_index < len(addrs):
            next_addr = addrs[st.session_state.step_index]
            st.markdown(f"**Step {st.session_state.step_index} / {len(addrs)}** | **Next Address:** `{next_addr}`")
        else:
            st.markdown(f"**Step {st.session_state.step_index} / {len(addrs)}** | 🎉 **All instructions processed!**")

    st.divider()


    # Layout: Snapshot and Metrics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Cache Snapshot")
        st.table(st.session_state.sim.cache)
        
        st.subheader("Trace Log")
        st.text_area("Log", "\n".join(st.session_state.sim.trace_log), height=200)

    with col2:
        st.subheader("Performance")
        # Handle cases where the cache might not have calculating methods yet
        if hasattr(st.session_state.sim, 'calculate_metrics'):
            metrics = st.session_state.sim.calculate_metrics()
            for k, v in metrics.items():
                st.metric(k, v)
        else:
            st.metric("Miss Count", getattr(st.session_state.sim, 'miss_count', 0))

if __name__ == "__main__":
    render_gui()