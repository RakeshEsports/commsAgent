"""
event_log.py — The agent's diary.

This file sets up "logging" — a way for the program to write messages
about what it's doing. Like a diary:

    "12:00:01 — Checked the microphone — PASS"
    "12:00:02 — Checked the headset — FAIL — device not found"

We write these in JSON format (a structured text format that looks like this):
    {"time": "12:00:01", "level": "INFO", "message": "Checked the microphone"}

This makes it easy for tools and humans to read the logs later.

How to use in other files:
    from src.loggingx.event_log import get_logger
    logger = get_logger("bootstrap")
    logger.info("Starting preflight checks")
    logger.error("Microphone not found!")
"""

import logging
import json
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """
    A custom formatter that turns each log message into a JSON line.

    Normal Python logging writes plain text like:
        INFO:bootstrap:Starting preflight checks

    Our formatter writes structured JSON like:
        {"timestamp": "2026-02-14T12:00:01Z", "level": "INFO", ...}
    """

    def format(self, record):
        # Build a dictionary (like a form with fields)
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,         # e.g. "INFO", "ERROR"
            "module": record.name,             # e.g. "bootstrap"
            "message": record.getMessage(),    # the actual text
        }

        # If extra data was attached, include it
        if hasattr(record, "detail"):
            log_entry["detail"] = record.detail

        # Convert the dictionary to a JSON text string
        return json.dumps(log_entry)


def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for the given module name.

    Usage:
        logger = get_logger("bootstrap")
        logger.info("Hello!")        # writes a JSON line with level=INFO
        logger.error("Oh no!")       # writes a JSON line with level=ERROR

    Args:
        module_name: A short name like "bootstrap" or "identity".
                     This appears in the log so you know WHERE the message came from.

    Returns:
        A configured logger that writes JSON to the console.
    """
    logger = logging.getLogger(module_name)

    # Only add a handler if this logger doesn't have one yet
    # (prevents duplicate log lines if get_logger is called twice)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Console handler — prints logs to the terminal
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)

    return logger
