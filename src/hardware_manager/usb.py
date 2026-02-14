"""
usb.py — Watches USB devices (plug/unplug).

This module uses `pyudev` to listen to Linux kernel events.
When you plug in a device, it wakes up and logs the event.
"""

import pyudev
from src.loggingx.event_log import get_logger

logger = get_logger("usb_monitor")

class USBWatcher:
    def __init__(self):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        
        # Filter: We only care about specific subsystems to avoid noise.
        # "sound" -> Audio devices (Headset, Phone)
        # "hid" -> Human Interface Devices (MiraBox, Keyboard)
        self.monitor.filter_by(subsystem='sound')
        self.monitor.filter_by(subsystem='hid')
        self.monitor.filter_by(subsystem='input')  # Catch-all for input devices

    def start_monitoring(self):
        """
        Start the loop. This function BLOCKS forever, so run it in a thread!
        """
        logger.info("USB Monitoring started...")
        
        for device in iter(self.monitor.poll, None):
            self._handle_event(device)

    def _handle_event(self, device):
        """
        Process a single USB event.
        """
        action = device.action
        
        # Basic Logging
        dev_path = device.device_path
        sys_name = device.sys_name
        
        # Try to get friendly names
        vendor = device.get('ID_VENDOR', 'Unknown')
        model = device.get('ID_MODEL', 'Unknown')
        
        msg = f"USB Event: {action.upper()} - {model} ({vendor}) at {sys_name}"
        
        # Log based on action
        if action == 'add':
            logger.info(f"➕ {msg}")
            self._check_specific_device(device, added=True)
            
        elif action == 'remove':
            logger.warning(f"➖ {msg}")
            self._check_specific_device(device, added=False)

    def _check_specific_device(self, device, added: bool):
        """
        Check if the device is one of our critical hardware pieces.
        """
        model = device.get('ID_MODEL', '')
        vendor = device.get('ID_VENDOR', '')
        
        # 1. Headset (KT USB Audio)
        if "KT_USB_Audio" in model or "KTMicro" in vendor:
            status = "CONNECTED" if added else "DISCONNECTED"
            logger.warning(f"🎧 HEADSET {status}!")
            
        # 2. Phone (ICUSBAUDIO7D)
        elif "ICUSBAUDIO7D" in model:
            status = "CONNECTED" if added else "DISCONNECTED"
            logger.warning(f"📞 PHONE LINE {status}!")
            
        # 3. MiraBox (Generic HID or specific ID?)
        # For now, just log any HID device change as potentially relevant
        elif device.subsystem == 'hid':
             status = "CONNECTED" if added else "DISCONNECTED"
             logger.info(f"🎮 CONTROL SURFACE {status} (Generic HID)")
