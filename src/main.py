"""
main.py — The entry point of the Agent.

This script just starts the Main Controller.
Usage:
    python3 src/main.py
"""

import sys
import os

# Ensure the current directory is in the python path
sys.path.append(os.getcwd())

from src.controller import MainController

def main():
    print("="*60)
    print("🤖 STARTING COMMS AGENT")
    print("="*60)

    try:
        app = MainController()
        app.run()
    except KeyboardInterrupt:
        print("\n\nNOTICE: Agent stopped by user.")
    except Exception as e:
        print(f"\n\nCRITICAL ERROR: {e}")
        # In production, we would log this to a file before crashing
        raise

if __name__ == "__main__":
    main()
