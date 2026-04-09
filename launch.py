"""Smart launcher for ScholAR - Finds available port automatically."""

import os
import sys
import socket
import subprocess
import time

def find_available_port(start_port=8501, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()

        if result != 0:  # Port is available
            return port

    return None

def main():
    print("=" * 60)
    print("  ScholAR - Autonomous Research Agent")
    print("=" * 60)
    print()

    # Find available port
    print("Finding available port...")
    port = find_available_port(8501, 10)

    if port is None:
        print("ERROR: Could not find an available port!")
        sys.exit(1)

    print(f"Using port: {port}")
    print()
    print("Launching Streamlit app...")
    print(f"Open browser to: http://localhost:{port}")
    print()
    print("Press Ctrl+C to stop")
    print()

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct path to streamlit app
    app_path = os.path.join(script_dir, "app", "streamlit_app.py")

    # Launch Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        app_path,
        f"--server.port={port}",
        "--server.address=127.0.0.1",
        "--client.showErrorDetails=true"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()

