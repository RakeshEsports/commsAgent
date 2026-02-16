"""
test_ui_renderer.py — Verification for Phase 8.
"""

import os
import sys
import pytest
from src.ui_renderer.view_model import ButtonColor
from src.ui_renderer.logic import resolve_priority
from src.ui_renderer.image_generator import ImageGenerator
from src.ui_renderer.renderer import MiraBoxRenderer, MiraBoxViewModel, ChannelView

def test_priority_logic():
    # 1. Hardware Error -> YELLOW
    view = resolve_priority(1, "Test", False, False, True, True)
    assert view.color == ButtonColor.YELLOW
    assert view.label == "ERROR"

    # 2. Offline -> BLACK
    view = resolve_priority(1, "Test", True, False, False, False)
    assert view.color == ButtonColor.BLACK
    assert view.label == "OFFLINE"

    # 3. Talking -> RED
    view = resolve_priority(1, "Director", True, False, True, False)
    assert view.color == ButtonColor.RED
    assert view.label == "Director"

    # 4. Muted -> GREY
    view = resolve_priority(1, "Director", False, True, True, False)
    assert view.color == ButtonColor.GREY
    assert view.label == "Director"

def test_image_generator():
    gen = ImageGenerator()
    output_path = "/tmp/test_image.jpg"
    
    gen.generate_button_image("LIVE", ButtonColor.RED, output_path)
    
    assert os.path.exists(output_path)
    # Optional: check file size > 0
    assert os.path.getsize(output_path) > 0
    
    # Cleanup
    if os.path.exists(output_path):
        os.remove(output_path)

def test_renderer_mock():
    # This should run without error even if no hardware attached
    renderer = MiraBoxRenderer()
    
    # Create a dummy View Model
    vm = MiraBoxViewModel(
        is_online=True,
        channels=[
            ChannelView(1, "Director", ButtonColor.RED, None),
            ChannelView(2, "Producer", ButtonColor.GREY, None)
        ]
    )
    
    # Try to render (should handle missing device gracefully)
    renderer.update(vm)
    
    # If no exception, test passes
    assert True
