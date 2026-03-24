import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.streamlit_app import render_gui

if __name__ == "__main__":
    render_gui()