"""Entry point to run the Streamlit app from repository root.
This file ensures `src` is discoverable as a package and imports the UI module.
"""
import sys
import os

# Ensure package 'src' can be imported when running from the repo root
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui import app_main  # noqa: F401 - module executes Streamlit UI on import
