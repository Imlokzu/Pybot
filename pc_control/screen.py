import logging
import pyautogui
from PIL import ImageGrab
import pytesseract
import cv2
import numpy as np
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ScreenCapture:
    """Клас для роботи зі скріншотами та розпізнаванням"""
    
    def __init__(self):
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def capture(self) -> str:
        """Робить скріншот екрану"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshot_dir}/screenshot_{timestamp}.png"
            
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            
            logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            raise
    
    def find_text_on_screen(self, text: str) -> tuple:
        """Знаходить текст на екрані за допомогою OCR"""
        try:
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            
            result = pytesseract.image_to_data(screenshot_np, output_type=pytesseract.Output.DICT)
            
            for i, word in enumerate(result['text']):
                if text.lower() in word.lower():
                    x = result['left'][i] + result['width'][i] // 2
                    y = result['top'][i] + result['height'][i] // 2
                    logger.info(f"Text '{text}' found at ({x}, {y})")
                    return (x, y)
            
            logger.warning(f"Text '{text}' not found on screen")
            return None
            
        except Exception as e:
            logger.error(f"Text search error: {e}")
            return None
