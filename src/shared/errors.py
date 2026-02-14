"""
errors.py — Custom error messages for the agent.

Python has a built-in system for errors called "exceptions".
When something goes wrong, you "raise" an exception, and the program
can decide what to do about it (retry, log it, shut down, etc.).

We create our OWN exception types so we can tell exactly WHAT went wrong.

Example usage:
    from src.shared.errors import IdentityError
    raise IdentityError("Identity file not found at /etc/ixg-agent/identity.json")
"""


class IdentityError(Exception):
    """
    Raised when the device identity file is missing or broken.

    Examples:
        - The file doesn't exist on disk
        - The file contains garbage (not valid JSON)
        - The file is missing required fields like device_id
    """
    pass


class PreflightError(Exception):
    """
    Raised when a CRITICAL preflight check fails.

    Examples:
        - No microphone detected
        - No headset speakers detected
        - MiraBox control surface not reachable
    """
    pass


class BootstrapError(Exception):
    """
    General wrapper for any bootstrap failure.

    This is the "catch-all" if something unexpected goes wrong during startup.
    """
    pass
