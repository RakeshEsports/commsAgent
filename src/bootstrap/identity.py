"""
identity.py — Loads the "Who am I?" file.

Every Pi box has a small JSON file on disk that contains its identity:
    {
        "device_id": "edge-box-042",
        "secret": "some-provisioning-secret",
        "profile": "operator-station-v1",
        "config_version": 0
    }

This module:
1. Opens that file
2. Checks it's valid (not broken/incomplete)
3. Returns the data in a neat Python object

If the file is missing or broken, it raises an IdentityError
(which means "stop everything — we don't know who we are").
"""

import json
from dataclasses import dataclass
from pathlib import Path

from src.shared.errors import IdentityError
from src.loggingx.event_log import get_logger

# Create a logger for this module
logger = get_logger("identity")


# --- Data Container ---
# A dataclass is like a form with named fields.
# Instead of using a plain dictionary like {"device_id": "...", "secret": "..."},
# we use this so Python can check we have the right fields.

@dataclass
class DeviceIdentity:
    """Holds the device's identity information."""
    device_id: str       # Unique name for this box, e.g. "edge-box-042"
    secret: str          # A password used to prove identity to the server
    profile: str         # What kind of station this is, e.g. "operator-station-v1"
    config_version: int  # Which version of settings this box last used (starts at 0)


# List of fields that MUST be in the identity file.
# If any of these are missing, the file is considered broken.
REQUIRED_FIELDS = ["device_id", "secret", "profile", "config_version"]


def load_identity(identity_path: str | Path) -> DeviceIdentity:
    """
    Read the identity file from disk and return a DeviceIdentity object.

    Args:
        identity_path: Where the identity file lives on disk.
                       Example: "/etc/ixg-agent/identity.json"

    Returns:
        A DeviceIdentity object with all fields filled in.

    Raises:
        IdentityError: If the file is missing, unreadable, or has missing fields.
    """
    # Convert to a Path object (makes file operations easier)
    path = Path(identity_path)

    # --------------------------------------------------
    # Check 1: Does the file exist?
    # --------------------------------------------------
    if not path.exists():
        message = f"Identity file not found: {path}"
        logger.error(message)
        raise IdentityError(message)

    # --------------------------------------------------
    # Check 2: Can we read it and is it valid JSON?
    # --------------------------------------------------
    try:
        # Open the file, read its contents, and parse the JSON
        with open(path, "r") as f:
            data = json.load(f)  # turns JSON text into a Python dictionary
    except json.JSONDecodeError as e:
        # The file exists but contains garbage (not proper JSON)
        message = f"Identity file is corrupt (invalid JSON): {path} — {e}"
        logger.error(message)
        raise IdentityError(message)
    except OSError as e:
        # Some other file reading problem (permissions, disk error, etc.)
        message = f"Cannot read identity file: {path} — {e}"
        logger.error(message)
        raise IdentityError(message)

    # --------------------------------------------------
    # Check 3: Does it have all the required fields?
    # --------------------------------------------------
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        message = f"Identity file is missing required fields: {missing}"
        logger.error(message)
        raise IdentityError(message)

    # --------------------------------------------------
    # All checks passed! Build and return the identity object.
    # --------------------------------------------------
    identity = DeviceIdentity(
        device_id=str(data["device_id"]),
        secret=str(data["secret"]),
        profile=str(data["profile"]),
        config_version=int(data["config_version"]),
    )

    logger.info(f"Identity loaded successfully: device_id={identity.device_id}")
    return identity
