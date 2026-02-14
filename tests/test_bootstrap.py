"""
test_bootstrap.py — Integration tests for the full bootstrap flow.

These test the "boss" function run_bootstrap() which calls identity + preflight.
We mock the preflight checks (since we have no real hardware) and test three
scenarios:

1. Everything works → success, state = DISCOVERING_HW
2. Identity file missing → fail, state = SAFE_MODE
3. Identity OK but mic missing → fail, state = SAFE_MODE
"""

import json
import pytest
from unittest.mock import patch
from pathlib import Path

from src.bootstrap import run_bootstrap, BootstrapOutcome
from src.bootstrap.preflight import PreflightResult
from src.shared.enums import AgentState, CheckSeverity, CheckStatus


# Helper
def make_result(name, severity, status):
    return PreflightResult(name, severity, status, f"Test: {name}")


def _all_checks_pass(*args, **kwargs):
    """Fake version of run_all_preflight_checks where everything passes."""
    from src.bootstrap.preflight import PreflightSummary
    from datetime import datetime, timezone
    return PreflightSummary(
        results=[
            make_result("headset_mic", CheckSeverity.CRITICAL, CheckStatus.PASS),
            make_result("headset_speakers", CheckSeverity.CRITICAL, CheckStatus.PASS),
            make_result("mirabox_reachable", CheckSeverity.CRITICAL, CheckStatus.PASS),
            make_result("phone_audio", CheckSeverity.WARNING, CheckStatus.PASS),
            make_result("clock_sync", CheckSeverity.WARNING, CheckStatus.PASS),
            make_result("config_cache_dir", CheckSeverity.WARNING, CheckStatus.PASS),
        ],
        has_critical_failure=False,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _mic_missing(*args, **kwargs):
    """Fake version of run_all_preflight_checks where mic is missing."""
    from src.bootstrap.preflight import PreflightSummary
    from datetime import datetime, timezone
    return PreflightSummary(
        results=[
            make_result("headset_mic", CheckSeverity.CRITICAL, CheckStatus.FAIL),
            make_result("headset_speakers", CheckSeverity.CRITICAL, CheckStatus.PASS),
            make_result("mirabox_reachable", CheckSeverity.CRITICAL, CheckStatus.PASS),
            make_result("phone_audio", CheckSeverity.WARNING, CheckStatus.PASS),
            make_result("clock_sync", CheckSeverity.WARNING, CheckStatus.PASS),
            make_result("config_cache_dir", CheckSeverity.WARNING, CheckStatus.PASS),
        ],
        has_critical_failure=True,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# ── Test 1: Everything works → success ──

@patch("src.bootstrap.run_all_preflight_checks", side_effect=_all_checks_pass)
def test_successful_bootstrap(mock_preflight, tmp_path: Path):
    """Valid identity + all checks pass → success, state=DISCOVERING_HW."""
    # Create a valid identity file
    identity_file = tmp_path / "identity.json"
    identity_file.write_text(json.dumps({
        "device_id": "test-box-001",
        "secret": "test-secret",
        "profile": "test-profile",
        "config_version": 1,
    }))

    outcome = run_bootstrap(identity_path=identity_file)

    assert outcome.success is True
    assert outcome.state == AgentState.DISCOVERING_HW
    assert outcome.identity is not None
    assert outcome.identity.device_id == "test-box-001"


# ── Test 2: Missing identity → safe mode ──

def test_missing_identity_goes_safe(tmp_path: Path):
    """Missing identity file → fail, state=SAFE_MODE."""
    missing_file = tmp_path / "no_such_file.json"

    outcome = run_bootstrap(identity_path=missing_file)

    assert outcome.success is False
    assert outcome.state == AgentState.SAFE_MODE
    assert outcome.identity is None
    assert "Identity failure" in outcome.reason


# ── Test 3: Identity OK but critical hardware missing → safe mode ──

@patch("src.bootstrap.run_all_preflight_checks", side_effect=_mic_missing)
def test_critical_hw_failure_goes_safe(mock_preflight, tmp_path: Path):
    """Identity OK but mic missing → fail, state=SAFE_MODE."""
    identity_file = tmp_path / "identity.json"
    identity_file.write_text(json.dumps({
        "device_id": "test-box-002",
        "secret": "test-secret",
        "profile": "test-profile",
        "config_version": 0,
    }))

    outcome = run_bootstrap(identity_path=identity_file)

    assert outcome.success is False
    assert outcome.state == AgentState.SAFE_MODE
    assert outcome.identity is not None  # identity loaded OK
    assert "Critical preflight failures" in outcome.reason
