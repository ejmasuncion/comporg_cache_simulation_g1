# main.py
import os
import sys

# Add the current directory to sys.path so 'logic' and 'gui' are discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.streamlit_app import render_gui

if __name__ == "__main__":
    # To run this, use: streamlit run main.py
    render_gui()