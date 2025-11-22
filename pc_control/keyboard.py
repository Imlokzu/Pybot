import logging
import pyautogui
import time

logger = logging.getLogger(__name__)


class KeyboardController:
    """Клас для контролю клавіатури"""
    
    def __init__(self):
        self.delay = 0.1
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """Набрати текст"""
        try:
            logger.info(f"Typing text: {text[:50]}...")
            pyautogui.typewrite(text, interval=interval)
            time.sleep(self.delay)
            return True
            
        except Exception as e:
            logger.error(f"Type text error: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Натиснути клавішу"""
        try:
            logger.info(f"Pressing key: {key}")
            pyautogui.press(key)
            time.sleep(self.delay)
            return True
            
        except Exception as e:
            logger.error(f"Press key error: {e}")
            return False
    
    def hotkey(self, *keys) -> bool:
        """
        Комбінація клавіш (Ctrl+C, Alt+Tab)
        
        Args:
            *keys: Клавіші для комбінації
            
        Returns:
            bool: Успіх операції
        """
        try:
            logger.info(f"Hotkey: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            time.sleep(self.delay)
            return True
            
        except Exception as e:
            logger.error(f"Hotkey error: {e}")
            return False
    
    def alt_enter(self) -> bool:
        """
        Alt+Enter комбінація
        
        Returns:
            bool: Успіх операції
        """
        try:
            logger.info("Alt+Enter pressed")
            pyautogui.hotkey('alt', 'enter')
            time.sleep(self.delay)
            return True
            
        except Exception as e:
            logger.error(f"Alt+Enter error: {e}")
            return False
    
    def enter_alt(self) -> bool:
        """
        Enter+Alt комбінація (те саме що Alt+Enter)
        
        Returns:
            bool: Успіх операції
        """
        try:
            logger.info("Enter+Alt pressed")
            pyautogui.hotkey('alt', 'enter')
            time.sleep(self.delay)
            return True
            
        except Exception as e:
            logger.error(f"Enter+Alt error: {e}")
            return False
    
    def write_unicode(self, text: str) -> bool:
        """Написати текст через буфер обміну (для Unicode)"""
        try:
            import pyperclip
            logger.info(f"Writing unicode text: {text[:50]}...")
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(self.delay)
            return True
            
        except Exception as e:
            logger.error(f"Unicode write error: {e}")
            return False
