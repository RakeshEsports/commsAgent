"""
ui_renderer/view_model.py — The "Menu" for the Screen.

This file defines the clean data structure that the Renderer (Painter)
uses to draw the screen. It hides all the messy internal details.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List

class ButtonColor(Enum):
    BLACK = "BLACK"     # Off / Offline
    GREY = "GREY"       # Idle / Muted
    RED = "RED"         # Live / Talking
    YELLOW = "YELLOW"   # Warning / Error
    GREEN = "GREEN"     # Listening (Future use)

@dataclass
class ChannelView:
    """
    What to show on ONE specific button/screen.
    """
    index: int          # Which button is this? (1-15)
    label: str          # Text on screen (e.g. "Director")
    color: ButtonColor  # Color of the light
    icon: str | None    # Path to icon (optional)

@dataclass
class MiraBoxViewModel:
    """
    The full picture for the entire device.
    """
    is_online: bool
    channels: List[ChannelView]
