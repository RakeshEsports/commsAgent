"""
preflight.py — The equipment checklist.

Before the Pi goes live, it runs a series of checks:
    ✅ Microphone plugged in?
    ✅ Headset speakers plugged in?
    ✅ MiraBox control surface reachable?
    ⚠️ Phone audio connected? (nice to have, not critical)
    ⚠️ System clock OK? (nice to have)
    ⚠️ Config cache folder exists? (nice to have)

Each check produces a result: PASS or FAIL.
Each check has a severity:
    CRITICAL = if this fails, we CANNOT go live
    WARNING  = if this fails, we note it but keep going

At the end, we collect all results into a summary.
"""

import subprocess
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from src.shared.enums import CheckSeverity, CheckStatus
from src.loggingx.event_log import get_logger

logger = get_logger("preflight")


# ──────────────────────────────────────────────────
# Data containers — hold results for each check
# ──────────────────────────────────────────────────

@dataclass
class PreflightResult:
    """
    The result of ONE check.

    Example:
        PreflightResult(
            check_name="headset_mic",
            severity=CheckSeverity.CRITICAL,
            status=CheckStatus.PASS,
            detail="Microphone device found"
        )
    """
    check_name: str             # Short name like "headset_mic"
    severity: CheckSeverity     # CRITICAL or WARNING
    status: CheckStatus         # PASS, FAIL, or SKIP
    detail: str                 # Human-readable explanation


@dataclass
class PreflightSummary:
    """
    The combined result of ALL checks.

    Fields:
        results: list of every individual check result
        has_critical_failure: True if ANY critical check failed
        timestamp: when the checks were run
    """
    results: list[PreflightResult] = field(default_factory=list)
    has_critical_failure: bool = False
    timestamp: str = ""


# ──────────────────────────────────────────────────
# Individual check functions
# Each function returns ONE PreflightResult
# ──────────────────────────────────────────────────

def check_audio_capture_device() -> PreflightResult:
    """
    Check: Is the Headset Microphone plugged in?

    We look for the specific USB device string "KT USB Audio".
    (Found at 'card 4' in aplay output).
    """
    check_name = "headset_mic"
    severity = CheckSeverity.CRITICAL

    try:
        # Run "arecord -l" to list capture devices
        result = subprocess.run(
            ["arecord", "-l"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Look for our specific headset device name
        if "KT USB Audio" in result.stdout:
            return PreflightResult(check_name, severity, CheckStatus.PASS,
                                   "Headset microphone found (KT USB Audio)")
        else:
            return PreflightResult(check_name, severity, CheckStatus.FAIL,
                                   "Headset microphone NOT found (KT USB Audio missing)")
    except FileNotFoundError:
        return PreflightResult(check_name, severity, CheckStatus.FAIL,
                               "arecord command not found")
    except Exception as e:
        return PreflightResult(check_name, severity, CheckStatus.FAIL,
                               f"Error checking headset mic: {e}")


def check_audio_playback_device() -> PreflightResult:
    """
    Check: Are the Headset Headphones plugged in?

    We look for the specific USB device string "KT USB Audio".
    (Found at 'card 4' in aplay output).
    """
    check_name = "headset_speakers"
    severity = CheckSeverity.CRITICAL

    try:
        # Run "aplay -l" to list playback devices
        result = subprocess.run(
            ["aplay", "-l"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if "KT USB Audio" in result.stdout:
            return PreflightResult(check_name, severity, CheckStatus.PASS,
                                   "Headset speakers found (KT USB Audio)")
        else:
            return PreflightResult(check_name, severity, CheckStatus.FAIL,
                                   "Headset speakers NOT found (KT USB Audio missing)")
    except FileNotFoundError:
        return PreflightResult(check_name, severity, CheckStatus.FAIL,
                               "aplay command not found")
    except Exception as e:
        return PreflightResult(check_name, severity, CheckStatus.FAIL,
                               f"Error checking headset speakers: {e}")


def check_mirabox_reachable() -> PreflightResult:
    """
    Check: Is the MiraBox control surface reachable?

    For now we check generic USB HID devices, but in production
    we would look for a specific Vendor ID/Product ID.
    """
    check_name = "mirabox_reachable"
    severity = CheckSeverity.CRITICAL

    # Placeholder: check if any HID devices exist
    hid_paths = [f"/dev/hidraw{i}" for i in range(10)]
    found = any(os.path.exists(p) for p in hid_paths)

    if found:
        return PreflightResult(check_name, severity, CheckStatus.PASS,
                               "Control surface found (USB HID detected)")
    else:
        return PreflightResult(check_name, severity, CheckStatus.FAIL,
                               "No control surface found (no /dev/hidraw detected)")


def check_phone_audio() -> PreflightResult:
    """
    Check: Is the Phone Audio line connected?

    We look for "ICUSBAUDIO7D" (Found at 'card 0' in aplay output).
    """
    check_name = "phone_audio"
    severity = CheckSeverity.WARNING

    try:
        result = subprocess.run(
            ["arecord", "-l"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if "ICUSBAUDIO7D" in result.stdout:
             return PreflightResult(check_name, severity, CheckStatus.PASS,
                                   "Phone audio line found (ICUSBAUDIO7D)")
        else:
            return PreflightResult(check_name, severity, CheckStatus.FAIL,
                                   "Phone audio line NOT found (ICUSBAUDIO7D missing)")
    except Exception as e:
        return PreflightResult(check_name, severity, CheckStatus.FAIL,
                               f"Error checking phone audio: {e}")


def check_clock_sync() -> PreflightResult:
    """
    Check: Is the system clock set to a reasonable date?

    This is WARNING only. A wrong clock can break security certificates,
    but the operator can still listen to audio.

    How it works:
        We check if the year is 2025 or later. If the Pi thinks it's 1970,
        that means the clock was never set (common on Pi without internet).
    """
    check_name = "clock_sync"
    severity = CheckSeverity.WARNING

    now = datetime.now(timezone.utc)
    if now.year >= 2025:
        return PreflightResult(check_name, severity, CheckStatus.PASS,
                               f"System clock looks reasonable: {now.isoformat()}")
    else:
        return PreflightResult(check_name, severity, CheckStatus.FAIL,
                               f"System clock may be wrong: {now.isoformat()} (year < 2025)")


def check_config_cache_dir(config_cache_dir: str | Path = "/var/cache/ixg-agent") -> PreflightResult:
    """
    Check: Does the config cache directory exist and is it writable?

    This is WARNING only. If we can't cache config, we'll still work
    but won't survive a reboot as smoothly.
    """
    check_name = "config_cache_dir"
    severity = CheckSeverity.WARNING

    cache_path = Path(config_cache_dir)
    if not cache_path.exists():
        return PreflightResult(check_name, severity, CheckStatus.FAIL,
                               f"Config cache directory does not exist: {cache_path}")

    if not os.access(cache_path, os.W_OK):
        return PreflightResult(check_name, severity, CheckStatus.FAIL,
                               f"Config cache directory is not writable: {cache_path}")

    return PreflightResult(check_name, severity, CheckStatus.PASS,
                           f"Config cache directory OK: {cache_path}")


# ──────────────────────────────────────────────────
# Run ALL checks and produce a summary
# ──────────────────────────────────────────────────

def run_all_preflight_checks(config_cache_dir: str | Path = "/var/cache/ixg-agent") -> PreflightSummary:
    """
    Run every preflight check and collect the results.

    Args:
        config_cache_dir: Path to the config cache directory to check.

    Returns:
        A PreflightSummary with all results and whether any critical check failed.
    """
    # Run each check and collect results
    results = [
        check_audio_capture_device(),
        check_audio_playback_device(),
        check_mirabox_reachable(),
        check_phone_audio(),
        check_clock_sync(),
        check_config_cache_dir(config_cache_dir),
    ]

    # Did ANY critical check fail?
    has_critical_failure = any(
        r.status == CheckStatus.FAIL and r.severity == CheckSeverity.CRITICAL
        for r in results
    )

    # Log each result
    for r in results:
        level = "error" if (r.status == CheckStatus.FAIL and r.severity == CheckSeverity.CRITICAL) else \
                "warning" if r.status == CheckStatus.FAIL else "info"
        getattr(logger, level)(
            f"[{r.severity.value}] {r.check_name}: {r.status.value} — {r.detail}"
        )

    summary = PreflightSummary(
        results=results,
        has_critical_failure=has_critical_failure,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    return summary
