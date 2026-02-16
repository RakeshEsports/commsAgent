"""
ui_renderer/renderer.py — The Painter.

This module takes the "View Model" (The Menu) and updates the physical device.
It handles:
1.  Connecting to the MiraBox (StreamDock).
2.  Generating Images (using image_generator.py).
3.  Sending Images to the device.
"""

import os
import sys
import logging
import time
from .view_model import MiraBoxViewModel, ChannelView
from .image_generator import ImageGenerator

# Ensure SteamDock is importable
# Assuming running from agent/ root
try:
    from SteamDock.DeviceManager import DeviceManager
    HAS_HARDWARE_LIB = True
except ImportError:
    HAS_HARDWARE_LIB = False
    logging.warning("SteamDock library not found. Running in Mock Mode.")

class MiraBoxRenderer:
    def __init__(self):
        self.device = None
        self.generator = ImageGenerator()
        self.logger = logging.getLogger("ui_renderer")
        
        # Connect to hardware
        self._connect()

    def _connect(self):
        """
        Attempt to find and connect to the StreamDock.
        """
        if not HAS_HARDWARE_LIB:
            return

        try:
            manager = DeviceManager()
            devices = manager.enumerate()
            if devices:
                self.device = devices[0]
                self.device.open()
                self.device.wakeScreen()
                self.logger.info(f"Connected to MiraBox: {self.device.id()}")
            else:
                self.logger.warning("No MiraBox device found.")
        except Exception as e:
            self.logger.error(f"Failed to connect to MiraBox: {e}")

    def update(self, view_model: MiraBoxViewModel):
        """
        Update the entire screen based on the ViewModel.
        """
        if not self.device:
            # Mock Mode: Just log what we would do
            # self.logger.debug(f"Mock Render: {view_model}")
            return

        # 1. Update Buttons
        for channel in view_model.channels:
            self._render_channel(channel)
            
        # 2. Refresh Screen (if needed)
        # self.device.refresh() needed? Usually set_key_image does it?
        # StreamDock implementation seems to handle it.

    def _render_channel(self, channel: ChannelView):
        """
        Render a single channel button.
        """
        # 1. Generate Image File
        # We need a temp path.
        temp_path = f"/tmp/mirabox_key_{channel.index}.jpg"
        
        # 2. Draw it
        self.generator.generate_button_image(
            label=channel.label,
            color=channel.color,
            output_path=temp_path
        )

        # 3. Send to Device
        try:
            # StreamDock expects key index 1-15?
            # Our ViewModel uses 1-based index ideally.
            self.device.set_key_image(channel.index, temp_path)
        except Exception as e:
            self.logger.error(f"Failed to update key {channel.index}: {e}")
        finally:
            # Cleanup temp file? 
            # Actually keeping it might be fine, or overwrite next time.
            pass

    def close(self):
        if self.device:
            self.device.close()
