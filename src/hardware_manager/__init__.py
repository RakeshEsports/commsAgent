"""
hardware_manager/__init__.py — The "Boss" of hardware monitoring.

This module starts two background workers:
1.  System Monitor (Checks CPU/RAM every 5 seconds)
2.  USB Monitor (Waits for plug/unplug events)
"""

import threading
import time

from src.loggingx.event_log import get_logger
from src.hardware_manager.system import get_system_metrics, log_system_health
from src.hardware_manager.usb import USBWatcher

logger = get_logger("hardware_manager")

class HardwareManager:
    """
    Orchestrates hardware monitoring threads.
    Runs continuously in the background.
    """
    def __init__(self):
        self._stop_event = threading.Event()
        self._usb_watcher = USBWatcher()
        
        # Threads
        self._system_thread = None
        self._usb_thread = None

    def start(self):
        """
        Start all monitoring threads.
        """
        logger.info("Starting Hardware Manager...")
        self._stop_event.clear()

        # 1. Start System Monitor Thread (Checks CPU/RAM every 5s)
        self._system_thread = threading.Thread(
            target=self._system_monitor_loop,
            name="SystemMonitorThread",
            daemon=True
        )
        self._system_thread.start()

        # 2. Start USB Monitor Thread (Waits for plug events)
        # Note: We create the USBWatcher instance once in __init__
        self._usb_thread = threading.Thread(
            target=self._usb_watcher.start_monitoring,
            name="USBMonitorThread",
            daemon=True
        )
        self._usb_thread.start()

        logger.info("Hardware Manager is RUNNING (Background threads started)")

    def stop(self):
        """
        Signal threads to stop.
        """
        logger.info("Stopping Hardware Manager...")
        self._stop_event.set()
        # Note: USB thread might ignore this as pyudev blocks, 
        # but daemon threads will die when main program exits anyway.

    def _system_monitor_loop(self):
        """
        Periodically check system health.
        """
        while not self._stop_event.is_set():
            try:
                # 1. Get stats
                metrics = get_system_metrics()
                # 2. Log them (warn if high)
                log_system_health(metrics)
            except Exception as e:
                logger.error(f"Error in System Monitor: {e}")

            # Sleep for 5 seconds (or until stopped)
            if self._stop_event.wait(timeout=5.0):
                break
        
        logger.info("System Monitor Loop stopped.")
