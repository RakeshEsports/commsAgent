"""
ui_renderer/image_generator.py — The Artist's Brush.

This module uses Pillow (PIL) to create the actual image files
that are sent to the MiraBox screens.
"""

from PIL import Image, ImageDraw, ImageFont
from .view_model import ButtonColor
import os

# Size of one button on MiraBox (StreamDock 293)
BUTTON_SIZE = (100, 100)

class ImageGenerator:
    def __init__(self):
        # We can load fonts here if needed
        # self.font = ImageFont.truetype("arial.ttf", 20)
        pass

    def generate_button_image(self, label: str, color: ButtonColor, output_path: str):
        """
        Create an image with a solid background color and centered text.
        Save it to output_path.
        """
        # 1. Determine RGB color
        bg_color = (50, 50, 50) # Default Grey
        if color == ButtonColor.RED:
            bg_color = (200, 0, 0)
        elif color == ButtonColor.GREEN:
            bg_color = (0, 200, 0)
        elif color == ButtonColor.YELLOW:
            bg_color = (200, 200, 0)
        elif color == ButtonColor.BLACK:
            bg_color = (0, 0, 0)

        # 2. Create Image
        img = Image.new('RGB', BUTTON_SIZE, color=bg_color)
        draw = ImageDraw.Draw(img)

        # 3. Draw Text (Centering is rough without font metrics, simple approximation)
        # Using default bitmap font if no truetype available
        # text_position = (10, 40)
        # draw.text(text_position, label, fill=(255, 255, 255))
        
        # Improvement: Centered Text
        # For now, just placing it in the middle roughly
        draw.text((10, 40), label, fill=(255, 255, 255))

        # 4. Save
        img.save(output_path, "JPEG", quality=95)
