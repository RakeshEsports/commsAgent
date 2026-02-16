
import time
import sys
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("manual_test")

# Import our new UI code
from src.ui_renderer.view_model import MiraBoxViewModel, ChannelView, ButtonColor
from src.ui_renderer.renderer import MiraBoxRenderer

def run_manual_test():
    logger.info("Initializing MiraBox Renderer...")
    renderer = MiraBoxRenderer()

    # 1. Test: OFFLINE (Black)
    logger.info("--- Test 1: Simulating OFFLINE ---")
    vm_offline = MiraBoxViewModel(
        is_online=False,
        channels=[
            ChannelView(1, "OFFLINE", ButtonColor.BLACK, None),
            ChannelView(2, "OFFLINE", ButtonColor.BLACK, None)
        ]
    )
    renderer.update(vm_offline)
    time.sleep(2)

    # 2. Test: ONLINE but MUTED (Grey)
    logger.info("--- Test 2: Simulating ONLINE (Muted) ---")
    vm_muted = MiraBoxViewModel(
        is_online=True,
        channels=[
            ChannelView(1, "Director", ButtonColor.GREY, None),
            ChannelView(2, "Producer", ButtonColor.GREY, None)
        ]
    )
    renderer.update(vm_muted)
    time.sleep(2)

    # 3. Test: TALKING (Red)
    logger.info("--- Test 3: Simulating TALKING (Red) ---")
    vm_talking = MiraBoxViewModel(
        is_online=True,
        channels=[
            ChannelView(1, "Director", ButtonColor.RED, None),
            ChannelView(2, "Producer", ButtonColor.GREY, None)
        ]
    )
    renderer.update(vm_talking)
    time.sleep(2)

    # 4. Test: ERROR (Yellow)
    logger.info("--- Test 4: Simulating ERROR (Yellow) ---")
    vm_error = MiraBoxViewModel(
        is_online=True,
        channels=[
            ChannelView(1, "ERROR", ButtonColor.YELLOW, None),
            ChannelView(2, "ERROR", ButtonColor.YELLOW, None)
        ]
    )
    renderer.update(vm_error)
    time.sleep(2)

    logger.info("--- Test Complete ---")
    renderer.close()

if __name__ == "__main__":
    run_manual_test()
