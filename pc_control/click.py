import logging
import pyautogui
import time

logger = logging.getLogger(__name__)


class ClickController:
    """Клас для контролю кліків миші"""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.delay = 0.5
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> bool:
        """Клік по координатам"""
        try:
            logger.info(f"Clicking at ({x}, {y}) with {button} button")
            pyautogui.click(x, y, clicks=clicks, button=button)
            time.sleep(self.delay)
            return True
            
        except Exception as e:
            logger.error(f"Click error: {e}")
            return False
    
    def double_click(self, x: int, y: int) -> bool:
        """Подвійний клік"""
        return self.click(x, y, clicks=2)
    
    def right_click(self, x: int, y: int) -> bool:
        """Клік правою кнопкою"""
        return self.click(x, y, button='right')
    
    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> bool:
        """Перетягування миші"""
        try:
            logger.info(f"Dragging from ({x1}, {y1}) to ({x2}, {y2})")
            pyautogui.moveTo(x1, y1)
            pyautogui.drag(x2 - x1, y2 - y1, duration=duration)
            time.sleep(self.delay)
            return True
            
        except Exception as e:
            logger.error(f"Drag error: {e}")
            return False
    
    def move_mouse(self, x: int, y: int) -> bool:
        """Рух миші без кліку"""
        try:
            logger.info(f"Moving mouse to ({x}, {y})")
            pyautogui.moveTo(x, y)
            return True
            
        except Exception as e:
            logger.error(f"Mouse move error: {e}")
            return False
