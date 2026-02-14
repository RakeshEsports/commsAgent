"""
bootstrap/__init__.py — The "Boss" that runs the whole startup sequence.

This is the main entry point for the bootstrap module.
It calls identity loading and preflight checks in order,
then decides: "Are we good to go, or should we stay in safe mode?"

How to use:
    from src.bootstrap import run_bootstrap

    outcome = run_bootstrap(
        identity_path="/etc/ixg-agent/identity.json",
        config_cache_dir="/var/cache/ixg-agent"
    )

    if outcome.success:
        print("Ready to proceed!")
    else:
        print(f"Staying in safe mode because: {outcome.reason}")
"""

import json
from dataclasses import dataclass
from pathlib import Path

from src.shared.enums import AgentState
from src.shared.errors import IdentityError
from src.bootstrap.identity import DeviceIdentity, load_identity
from src.bootstrap.preflight import PreflightSummary, run_all_preflight_checks
from src.loggingx.event_log import get_logger

logger = get_logger("bootstrap")


# ──────────────────────────────────────────────────
# Bootstrap Outcome — the final answer from bootstrap
# ──────────────────────────────────────────────────

@dataclass
class BootstrapOutcome:
    """
    The result of the entire bootstrap process.

    Fields:
        success: True if the Pi is ready to proceed, False if stuck in safe mode
        state: Which stage the Pi should move to next
        identity: The device identity (or None if identity loading failed)
        preflight: The full preflight summary (or None if it never ran)
        reason: Human-readable explanation of the outcome
    """
    success: bool
    state: AgentState
    identity: DeviceIdentity | None
    preflight: PreflightSummary | None
    reason: str


# ──────────────────────────────────────────────────
# Main bootstrap function
# ──────────────────────────────────────────────────

def run_bootstrap(
    identity_path: str | Path = "/etc/ixg-agent/identity.json",
    config_cache_dir: str | Path = "/var/cache/ixg-agent",
    preflight_save_path: str | Path | None = None,
) -> BootstrapOutcome:
    """
    Run the full bootstrap sequence:
        1. Load identity ("who am I?")
        2. Run preflight checks ("is my equipment ready?")
        3. Decide: proceed or stay in safe mode

    Args:
        identity_path: Where the identity JSON file is on disk.
        config_cache_dir: Where cached config files are stored.
        preflight_save_path: Optional path to save the preflight summary for later comparison.

    Returns:
        A BootstrapOutcome telling the rest of the agent what to do.
    """
    logger.info("=== BOOTSTRAP START ===")

    # ── Step 1: Load Identity ──────────────────────
    logger.info("Step 1: Loading device identity...")
    identity = None
    try:
        identity = load_identity(identity_path)
        logger.info(f"Identity OK: device_id={identity.device_id}")
    except IdentityError as e:
        # Identity is MISSING or BROKEN — this is a hard failure.
        # We cannot continue without knowing who we are.
        reason = f"Identity failure: {e}"
        logger.error(reason)
        logger.error("BOOTSTRAP RESULT: SAFE_MODE (identity failure)")
        return BootstrapOutcome(
            success=False,
            state=AgentState.SAFE_MODE,
            identity=None,
            preflight=None,
            reason=reason,
        )

    # ── Step 2: Run Preflight Checks ───────────────
    logger.info("Step 2: Running preflight checks...")
    preflight_summary = run_all_preflight_checks(config_cache_dir=config_cache_dir)

    # Save the preflight summary to disk (for incident comparison later)
    if preflight_save_path:
        _save_preflight_summary(preflight_summary, preflight_save_path)

    # ── Step 3: Decide ─────────────────────────────
    if preflight_summary.has_critical_failure:
        # At least one critical check failed (e.g. no mic).
        # We stay in safe mode — can listen but cannot transmit.
        failed_critical = [
            r for r in preflight_summary.results
            if r.status.value == "FAIL" and r.severity.value == "CRITICAL"
        ]
        failed_names = [r.check_name for r in failed_critical]
        reason = f"Critical preflight failures: {failed_names}"
        logger.error(reason)
        logger.error("BOOTSTRAP RESULT: SAFE_MODE (critical hardware missing)")
        return BootstrapOutcome(
            success=False,
            state=AgentState.SAFE_MODE,
            identity=identity,
            preflight=preflight_summary,
            reason=reason,
        )

    # ── All good! ──────────────────────────────────
    reason = "All critical checks passed"
    logger.info(f"BOOTSTRAP RESULT: DISCOVERING_HW ({reason})")
    return BootstrapOutcome(
        success=True,
        state=AgentState.DISCOVERING_HW,
        identity=identity,
        preflight=preflight_summary,
        reason=reason,
    )


def _save_preflight_summary(summary: PreflightSummary, save_path: str | Path) -> None:
    """
    Save the preflight summary to a JSON file on disk.

    This is useful for support teams: they can compare today's preflight
    with yesterday's to see what changed.
    """
    path = Path(save_path)
    try:
        # Make sure the parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert the summary into a dictionary we can save as JSON
        data = {
            "timestamp": summary.timestamp,
            "has_critical_failure": summary.has_critical_failure,
            "results": [
                {
                    "check_name": r.check_name,
                    "severity": r.severity.value,
                    "status": r.status.value,
                    "detail": r.detail,
                }
                for r in summary.results
            ],
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Preflight summary saved to {path}")
    except Exception as e:
        # Saving is best-effort — don't crash just because we can't save logs
        logger.warning(f"Could not save preflight summary: {e}")
