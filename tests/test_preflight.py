"""
test_preflight.py — Tests for the preflight checklist.

Since we're not running on a real Raspberry Pi, we "mock" (fake) the hardware
checks. This lets us test the logic without needing actual devices plugged in.

We use unittest.mock.patch to replace the real check functions with fake ones
that return whatever result we want.
"""

import pytest
from unittest.mock import patch

from src.bootstrap.preflight import (
    PreflightResult,
    PreflightSummary,
    run_all_preflight_checks,
)
from src.shared.enums import CheckSeverity, CheckStatus


# ── Helper: create a fake check result ──

def make_result(name: str, severity: CheckSeverity, status: CheckStatus) -> PreflightResult:
    """Helper to quickly make a PreflightResult for testing."""
    return PreflightResult(
        check_name=name,
        severity=severity,
        status=status,
        detail=f"Test result for {name}",
    )


# ── Test 1: All checks pass → no critical failure ──

@patch("src.bootstrap.preflight.check_config_cache_dir")
@patch("src.bootstrap.preflight.check_clock_sync")
@patch("src.bootstrap.preflight.check_phone_audio")
@patch("src.bootstrap.preflight.check_mirabox_reachable")
@patch("src.bootstrap.preflight.check_audio_playback_device")
@patch("src.bootstrap.preflight.check_audio_capture_device")
def test_all_checks_pass(
    mock_capture, mock_playback, mock_mirabox,
    mock_phone, mock_clock, mock_cache
):
    """When all devices are present, summary should have no critical failures."""
    # Set up: all checks return PASS
    mock_capture.return_value = make_result("headset_mic", CheckSeverity.CRITICAL, CheckStatus.PASS)
    mock_playback.return_value = make_result("headset_speakers", CheckSeverity.CRITICAL, CheckStatus.PASS)
    mock_mirabox.return_value = make_result("mirabox_reachable", CheckSeverity.CRITICAL, CheckStatus.PASS)
    mock_phone.return_value = make_result("phone_audio", CheckSeverity.WARNING, CheckStatus.PASS)
    mock_clock.return_value = make_result("clock_sync", CheckSeverity.WARNING, CheckStatus.PASS)
    mock_cache.return_value = make_result("config_cache_dir", CheckSeverity.WARNING, CheckStatus.PASS)

    # Run
    summary = run_all_preflight_checks()

    # Check
    assert summary.has_critical_failure is False
    assert len(summary.results) == 6
    assert all(r.status == CheckStatus.PASS for r in summary.results)


# ── Test 2: Critical failure (mic missing) → blocks boot ──

@patch("src.bootstrap.preflight.check_config_cache_dir")
@patch("src.bootstrap.preflight.check_clock_sync")
@patch("src.bootstrap.preflight.check_phone_audio")
@patch("src.bootstrap.preflight.check_mirabox_reachable")
@patch("src.bootstrap.preflight.check_audio_playback_device")
@patch("src.bootstrap.preflight.check_audio_capture_device")
def test_critical_failure_blocks(
    mock_capture, mock_playback, mock_mirabox,
    mock_phone, mock_clock, mock_cache
):
    """When mic is missing (CRITICAL FAIL), summary must flag critical failure."""
    # Mic is MISSING → FAIL
    mock_capture.return_value = make_result("headset_mic", CheckSeverity.CRITICAL, CheckStatus.FAIL)
    # Everything else passes
    mock_playback.return_value = make_result("headset_speakers", CheckSeverity.CRITICAL, CheckStatus.PASS)
    mock_mirabox.return_value = make_result("mirabox_reachable", CheckSeverity.CRITICAL, CheckStatus.PASS)
    mock_phone.return_value = make_result("phone_audio", CheckSeverity.WARNING, CheckStatus.PASS)
    mock_clock.return_value = make_result("clock_sync", CheckSeverity.WARNING, CheckStatus.PASS)
    mock_cache.return_value = make_result("config_cache_dir", CheckSeverity.WARNING, CheckStatus.PASS)

    summary = run_all_preflight_checks()

    assert summary.has_critical_failure is True


# ── Test 3: Warning failure (phone missing) → does NOT block boot ──

@patch("src.bootstrap.preflight.check_config_cache_dir")
@patch("src.bootstrap.preflight.check_clock_sync")
@patch("src.bootstrap.preflight.check_phone_audio")
@patch("src.bootstrap.preflight.check_mirabox_reachable")
@patch("src.bootstrap.preflight.check_audio_playback_device")
@patch("src.bootstrap.preflight.check_audio_capture_device")
def test_warning_does_not_block(
    mock_capture, mock_playback, mock_mirabox,
    mock_phone, mock_clock, mock_cache
):
    """When phone is missing (WARNING FAIL), boot should NOT be blocked."""
    # All critical checks pass
    mock_capture.return_value = make_result("headset_mic", CheckSeverity.CRITICAL, CheckStatus.PASS)
    mock_playback.return_value = make_result("headset_speakers", CheckSeverity.CRITICAL, CheckStatus.PASS)
    mock_mirabox.return_value = make_result("mirabox_reachable", CheckSeverity.CRITICAL, CheckStatus.PASS)
    # Phone is MISSING → FAIL, but it's only WARNING
    mock_phone.return_value = make_result("phone_audio", CheckSeverity.WARNING, CheckStatus.FAIL)
    mock_clock.return_value = make_result("clock_sync", CheckSeverity.WARNING, CheckStatus.PASS)
    mock_cache.return_value = make_result("config_cache_dir", CheckSeverity.WARNING, CheckStatus.PASS)

    summary = run_all_preflight_checks()

    # Phone is missing but it's only a warning, so no critical failure
    assert summary.has_critical_failure is False
