"""
system.py — Watches CPU, Memory, and Disk usage.

This module uses `psutil` to fetch system metrics.
It helps us know if the Pi is overloaded or running out of space.
"""

import psutil
from dataclasses import dataclass
from src.loggingx.event_log import get_logger

logger = get_logger("system_monitor")

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_percent: float

def get_system_metrics() -> SystemMetrics:
    """
    Fetch current system usage stats.
    
    Returns:
        SystemMetrics object with cpu, memory, and disk usage percentages.
    """
    # cpu_percent(interval=None) returns immediate result since last call.
    # The very first call returns 0.0, but subsequent calls are accurate.
    # This is non-blocking, which is good for our loop.
    cpu = psutil.cpu_percent(interval=None)
    
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    
    return SystemMetrics(cpu, mem, disk)

def log_system_health(metrics: SystemMetrics):
    """
    Log the health status.
    If usage is high (>80%), log a WARNING.
    Otherwise, log INFO.
    """
    # Thresholds for warning
    CPU_WARN_THRESHOLD = 80.0
    MEM_WARN_THRESHOLD = 80.0
    DISK_WARN_THRESHOLD = 90.0

    msg = (f"System Health: CPU={metrics.cpu_percent}% | "
           f"RAM={metrics.memory_percent}% | "
           f"Disk={metrics.disk_percent}%")

    if (metrics.cpu_percent > CPU_WARN_THRESHOLD or 
        metrics.memory_percent > MEM_WARN_THRESHOLD or 
        metrics.disk_percent > DISK_WARN_THRESHOLD):
        logger.warning(f"HIGH LOAD DETECTED: {msg}")
    else:
        logger.info(msg)
