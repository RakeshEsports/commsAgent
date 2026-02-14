"""
real_boot.py — Runs the bootstrap on the Real Pi hardware.

Usage:
    python3 real_boot.py

It will:
1. Create a temporary identity (so we don't need a real file yet)
2. Run all checks against YOUR REAL HARDWARE
3. Print the results clearly to the screen
"""

from src.bootstrap import run_bootstrap, BootstrapOutcome
from src.shared.enums import AgentState, CheckStatus, CheckSeverity
from pathlib import Path
import json
import os

def main():
    print("="*60)
    print("🚀 STARTING REAL HARDWARE VERIFICATION")
    print("="*60)

    # 1. Create a fake identity file so that part passes
    # We write it to a temp path
    identity_path = Path("temp_identity.json")
    with open(identity_path, "w") as f:
        json.dump({
            "device_id": "real-pi-test",
            "secret": "test",
            "profile": "test",
            "config_version": 1
        }, f)
    
    print("✅ Created temporary identity file")

    # 2. Run the real bootstrap
    print("🔄 Running bootstrap... (checking hardware)")
    
    # We pass the path to the current directory for cache check so it passes permissions
    outcome = run_bootstrap(
        identity_path=identity_path,
        config_cache_dir=os.getcwd() 
    )

    # 3. Clean up
    os.remove(identity_path)

    # 4. Report Results
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)

    # Print each check result
    for result in outcome.preflight.results:
        icon = "✅" if result.status == CheckStatus.PASS else "❌"
        # Colorize output if supported
        print(f"{icon} {result.check_name:<20} : {result.status.value}")
        print(f"      ↳ {result.detail}")
    
    print("-" * 60)
    
    if outcome.success:
        print("\n🎉 SUCCESS! The Pi is ready to go LIVE.")
        print(f"State: {outcome.state.value}")
    else:
        print("\n⛔ FAILED. The Pi is stuck in SAFE_MODE.")
        print(f"Reason: {outcome.reason}")

if __name__ == "__main__":
    main()
