"""
controller/__init__.py — The Brain of the Agent.

This is the main class that runs the show. It:
1.  Runs Bootstrap (Security/Hardware Check)
2.  Starts Hardware Manager (Monitoring)
3.  Enters the Main Loop (Wait for calls)
"""

import time
import sys
import threading
from src.shared.enums import AgentState
from src.loggingx.event_log import get_logger
from src.bootstrap import run_bootstrap
from src.hardware_manager import HardwareManager

logger = get_logger("controller")

class MainController:
    def __init__(self):
        self.state = AgentState.BOOTING
        self.hardware_manager = None
        self._stop_event = threading.Event()

    def boot(self):
        """
        Phase 1: Bootstrap.
        Check identity and hardware BEFORE we do anything else.
        """
        logger.info("=== PHASE 1: BOOTSTRAP ===")
        
        # We assume identity details are handled by bootstrap internally
        # (For production, we'd pass real paths here, but defaults work for now)
        # FIX: Force local path for development so we don't look in /etc/
        import os
        from pathlib import Path
        
        cwd = os.getcwd()
        outcome = run_bootstrap(
            identity_path=Path(cwd) / "identity.json",
            config_cache_dir=cwd
        )
        
        if outcome.success:
            logger.info(f"Bootstrap PASS. Moving to {outcome.state.value}...")
            self.state = outcome.state
            return True
        else:
            logger.critical(f"Bootstrap FAILED. Reason: {outcome.reason}")
            self.state = AgentState.SAFE_MODE
            return False

    def start_services(self):
        """
        Phase 2: Start Background Services.
        """
        if self.state == AgentState.SAFE_MODE:
            logger.warning("Agent is in SAFE MODE. Skipping hardware monitoring.")
            return

        logger.info("=== PHASE 2: STARTING SERVICES ===")
        
        # Start Hardware Manager
        self.hardware_manager = HardwareManager()
        self.hardware_manager.start()
        
        self.state = AgentState.READY
        logger.info("Services Started. Agent is READY.")

    def run(self):
        """
        Phase 3: Main Loop.
        Keep the program running forever (until stopped).
        """
        # 1. Boot
        if not self.boot():
            logger.error("System halted due to bootstrap failure.")
            return

        # 2. Start Services
        self.start_services()

        # 3. Main Loop
        logger.info("=== PHASE 3: MAIN LOOP ===")
        logger.info("Waiting for calls... (Press Ctrl+C to stop)")
        
        try:
            while not self._stop_event.is_set():
                # In the future, we will check for incoming calls here.
                # For now, just sleep and save CPU.
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping agent (User Interrupt)...")
        finally:
            self.stop()

    def stop(self):
        """
        Clean shutdown.
        """
        logger.info("Stopping all services...")
        if self.hardware_manager:
            self.hardware_manager.stop()
        logger.info("Agent Stopped.")

if __name__ == "__main__":
    # Test run
    controller = MainController()
    controller.run()
