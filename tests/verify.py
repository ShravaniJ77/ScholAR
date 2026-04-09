"""Quick verification script to ensure ScholAR is ready to run."""

import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[NO] Python {version.major}.{version.minor} - Need 3.8+")
        return False
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_imports():
    """Check if all required modules can be imported."""
    required_modules = {
        "streamlit": "streamlit",
        "pandas": "pandas",
        "plotly": "plotly",
        "networkx": "networkx",
        "requests": "requests",
    }

    all_good = True
    for module_name, import_name in required_modules.items():
        try:
            __import__(import_name)
            print(f"[OK] {module_name}")
        except ImportError:
            print(f"[NO] {module_name} - Run: pip install {module_name}")
            all_good = False

    return all_good

def check_local_modules():
    """Check if local modules exist and are syntactically correct."""
    local_modules = ["agent", "config", "models", "mock_data"]

    all_good = True
    for module in local_modules:
        try:
            code = open(f"{module}.py").read()
            compile(code, f"{module}.py", "exec")
            print(f"[OK] {module}.py")
        except Exception as e:
            print(f"[NO] {module}.py - {str(e)[:50]}")
            all_good = False

    return all_good

def main():
    print("=" * 50)
    print("  ScholAR - Verification")
    print("=" * 50)
    print("")

    print("Checking Python...")
    py_ok = check_python_version()
    print("")

    print("Checking dependencies...")
    deps_ok = check_imports()
    print("")

    print("Checking modules...")
    local_ok = check_local_modules()
    print("")

    print("=" * 50)
    if py_ok and deps_ok and local_ok:
        print("SUCCESS: Ready to run!")
        print("")
        print("To start:")
        print("  streamlit run streamlit_app.py")
        print("")
        return 0
    else:
        print("ERROR: Fix issues above")
        print("")
        print("Install dependencies:")
        print("  pip install -r requirements.txt")
        print("")
        return 1

if __name__ == "__main__":
    sys.exit(main())
