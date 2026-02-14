"""
test_identity.py — Tests for the identity loader.

These tests check that identity.py works correctly in 4 scenarios:
1. A valid identity file → should load successfully
2. File is missing → should raise IdentityError
3. File has broken JSON → should raise IdentityError
4. File is missing required fields → should raise IdentityError

We use pytest and Python's tmp_path fixture to create temporary test files.
"""

import json
import pytest
from pathlib import Path

from src.bootstrap.identity import load_identity, DeviceIdentity
from src.shared.errors import IdentityError


# ── Test 1: Valid identity file loads correctly ──

def test_load_valid_identity(tmp_path: Path):
    """
    If the file exists and has all required fields,
    load_identity should return a DeviceIdentity with the correct values.
    """
    # Arrange: create a valid identity file in a temporary directory
    identity_file = tmp_path / "identity.json"
    identity_file.write_text(json.dumps({
        "device_id": "edge-box-042",
        "secret": "my-secret-password",
        "profile": "operator-station-v1",
        "config_version": 3,
    }))

    # Act: load it
    result = load_identity(identity_file)

    # Assert: check the returned object has the right values
    assert isinstance(result, DeviceIdentity)
    assert result.device_id == "edge-box-042"
    assert result.secret == "my-secret-password"
    assert result.profile == "operator-station-v1"
    assert result.config_version == 3


# ── Test 2: Missing file raises IdentityError ──

def test_load_missing_file(tmp_path: Path):
    """
    If the file does not exist,
    load_identity should raise an IdentityError.
    """
    missing_file = tmp_path / "does_not_exist.json"

    with pytest.raises(IdentityError):
        load_identity(missing_file)


# ── Test 3: Corrupt (invalid JSON) raises IdentityError ──

def test_load_corrupt_json(tmp_path: Path):
    """
    If the file exists but contains garbage (not valid JSON),
    load_identity should raise an IdentityError.
    """
    corrupt_file = tmp_path / "identity.json"
    corrupt_file.write_text("this is not json {{{!!!")

    with pytest.raises(IdentityError):
        load_identity(corrupt_file)


# ── Test 4: Missing required fields raises IdentityError ──

def test_load_missing_fields(tmp_path: Path):
    """
    If the file is valid JSON but is missing required fields,
    load_identity should raise an IdentityError.
    """
    incomplete_file = tmp_path / "identity.json"
    incomplete_file.write_text(json.dumps({
        "device_id": "edge-box-042",
        # "secret" is missing!
        # "profile" is missing!
        "config_version": 0,
    }))

    with pytest.raises(IdentityError):
        load_identity(incomplete_file)
