"""
run_manager.py — Test the Hardware Manager.

This script starts the background monitoring service.
It runs for 30 seconds, giving you time to PLUG/UNPLUG devices.
"""

import time
import sys
from src.hardware_manager import HardwareManager

def main():
    print("="*60)
    print("🔧 HARDWARE MANAGER TEST (30 Seconds)")
    print("="*60)
    print("Starting background threads...")

    manager = HardwareManager()
    manager.start()

    print("\n✅ Manager is running!")
    print("👉 Try UNPLUGGING the Headset or plugging in a USB drive.")
    print("👉 Watch the logs below for 'USB Event' or 'System Health'.")
    print("-" * 60)

    try:
        # Run for 30 seconds
        for i in range(30, 0, -1):
            sys.stdout.write(f"\rTime remaining: {i}s   ")
            sys.stdout.flush()
            time.sleep(1)
        print("\n" + "-" * 60)
        print("Stopping...")
    except KeyboardInterrupt:
        print("\nStopping (User interrupt)...")
    finally:
        manager.stop()
        print("✅ Manager stopped.")

if __name__ == "__main__":
    main()
