"""
ui_renderer/logic.py — The Referee.

This file decides "Who Wins?".
Example: If you are Talking (Red) but the Internet dies (Black), who wins?
Answer: The Referee says BLACK (Safety First).
"""

from .view_model import ButtonColor, ChannelView

def resolve_priority(
    index: int,
    label: str,
    is_talking: bool,
    is_muted: bool,
    is_online: bool,
    has_hardware_error: bool
) -> ChannelView:
    """
    Decide the final color and text for a button based on conflicting inputs.
    """
    
    # Rule 1: Hardware Error is Highest Priority (YELLOW)
    if has_hardware_error:
        return ChannelView(index, "ERROR", ButtonColor.YELLOW, None)

    # Rule 2: Offline is Second Priority (BLACK/OFF)
    if not is_online:
        return ChannelView(index, "OFFLINE", ButtonColor.BLACK, None)

    # Rule 3: Talking (RED) overrides Mute
    if is_talking:
        return ChannelView(index, label, ButtonColor.RED, None)

    # Rule 4: Muted (GREY)
    if is_muted:
        return ChannelView(index, label, ButtonColor.GREY, None)

    # Default: Idle (Green or Grey depending on design preference)
    # We'll use GREY for idle/listening as a safe default
    return ChannelView(index, label, ButtonColor.GREY, None)
