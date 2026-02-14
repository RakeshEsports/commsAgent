"""
enums.py — Labels used across the whole agent.

Think of these like traffic light colors. Instead of writing the word "PASS"
as a plain string (where you might accidentally mistype it as "pass" or "Pass"),
we define it once here and use the label everywhere.

How to use in other files:
    from src.shared.enums import AgentState, CheckSeverity, CheckStatus
    state = AgentState.BOOTING
"""

from enum import Enum


# --- Agent State Machine ---
# These are the "stages" the Pi goes through from power-on to fully working.
# Only ONE of these can be active at a time.

class AgentState(Enum):
    BOOTING = "BOOTING"                  # Just powered on, doing nothing yet
    DISCOVERING_HW = "DISCOVERING_HW"    # Looking for plugged-in devices
    REGISTERING = "REGISTERING"          # Telling the control plane "I exist"
    SYNCING_CONFIG = "SYNCING_CONFIG"    # Downloading settings from server
    READY = "READY"                      # All set, but talk is still off
    LIVE = "LIVE"                        # Normal operation, talk controls active
    DEGRADED = "DEGRADED"               # Something broke, but we can still listen
    SAFE_MODE = "SAFE_MODE"             # Emergency: talk is forcibly OFF


# --- Check Severity ---
# When we run a check (like "is the mic plugged in?"), how serious is it
# if the check fails?

class CheckSeverity(Enum):
    CRITICAL = "CRITICAL"  # If this fails, we CANNOT go live (e.g. no mic)
    WARNING = "WARNING"    # If this fails, we note it but keep going (e.g. no webcam)


# --- Check Status ---
# The result of running one check.

class CheckStatus(Enum):
    PASS = "PASS"    # Check succeeded — everything is fine
    FAIL = "FAIL"    # Check failed — something is wrong
    SKIP = "SKIP"    # Check was skipped (e.g. not applicable right now)


# --- Talk Mode ---
# How the operator's talk button works on a partyline (intercom channel).

class TalkMode(Enum):
    PTT = "PTT"      # Push-To-Talk: hold the button to talk, release to stop
    LATCH = "LATCH"  # Latch: press once to start talking, press again to stop
