#!/usr/bin/env python3
"""
ScholAR - Autonomous Research Agent
Main entry point for the Streamlit application
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app"""
    app_path = os.path.join(os.path.dirname(__file__), 'app', 'streamlit_app.py')

    try:
        subprocess.run(
            ['streamlit', 'run', app_path],
            check=True
        )
    except FileNotFoundError:
        print("Error: Streamlit not installed. Run: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()
