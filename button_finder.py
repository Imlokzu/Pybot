import logging
import cv2
import numpy as np
from pc_control.screen import ScreenCapture
from pc_control.click import ClickController

logger = logging.getLogger(__name__)


class ButtonFinder:
    """Пошук та клік по кнопкам на екрані"""
    
    def __init__(self):
        self.screen = ScreenCapture()
        self.click = ClickController()
    
    def find_button_by_text(self, button_text: str, threshold: float = 0.7) -> tuple[bool, tuple]:
        """
        Знаходить кнопку за текстом
        
        Args:
            button_text: Текст на кнопці (напр. "Accept All")
            threshold: Поріг впевненості для OCR
            
        Returns:
            (знайдено, координати)
        """
        try:
            logger.info(f"Searching for button: {button_text}")
            
            # Беремо скріншот
            screenshot_path = self.screen.capture()
            
            # Читаємо зображення
            image = cv2.imread(screenshot_path)
            if image is None:
                logger.error(f"Failed to read screenshot: {screenshot_path}")
                return False, (0, 0)
            
            # Конвертуємо в сірий
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Розпізнаємо текст
            try:
                import pytesseract
                text_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
                
                # Шукаємо текст
                for i, text in enumerate(text_data['text']):
                    if button_text.lower() in text.lower():
                        # Отримуємо координати
                        x = text_data['left'][i]
                        y = text_data['top'][i]
                        w = text_data['width'][i]
                        h = text_data['height'][i]
                        
                        # Центр кнопки
                        center_x = x + w // 2
                        center_y = y + h // 2
                        
                        logger.info(f"Button found at ({center_x}, {center_y}): {text}")
                        return True, (center_x, center_y)
            
            except Exception as e:
                logger.error(f"OCR error: {e}")
                return False, (0, 0)
            
            logger.warning(f"Button not found: {button_text}")
            return False, (0, 0)
        
        except Exception as e:
            logger.error(f"Button finder error: {e}")
            return False, (0, 0)
    
    def find_and_click_button(self, button_text: str) -> str:
        """
        Знаходить кнопку та натискає на неї
        
        Args:
            button_text: Текст на кнопці
            
        Returns:
            str: Результат операції
        """
        try:
            logger.info(f"Finding and clicking button: {button_text}")
            
            found, (x, y) = self.find_button_by_text(button_text)
            
            if not found or (x == 0 and y == 0):
                return f"❌ Кнопка '{button_text}' не знайдена на екрані"
            
            # Натискаємо на кнопку
            self.click.click(x, y)
            
            logger.info(f"Button clicked: {button_text} at ({x}, {y})")
            return f"✅ Кнопка '{button_text}' натиснута на ({x}, {y})"
        
        except Exception as e:
            logger.error(f"Click button error: {e}")
            return f"❌ Помилка: {str(e)}"
    
    def find_button_by_color(self, color_bgr: tuple, tolerance: int = 30) -> tuple[bool, tuple]:
        """
        Знаходить кнопку за кольором
        
        Args:
            color_bgr: Колір в форматі BGR (напр. (0, 255, 0) для зеленого)
            tolerance: Допуск кольору
            
        Returns:
            (знайдено, координати)
        """
        try:
            logger.info(f"Searching for button by color: {color_bgr}")
            
            # Беремо скріншот
            screenshot_path = self.screen.capture()
            
            # Читаємо зображення
            image = cv2.imread(screenshot_path)
            if image is None:
                logger.error(f"Failed to read screenshot: {screenshot_path}")
                return False, (0, 0)
            
            # Створюємо маску для кольору
            lower = np.array([max(0, c - tolerance) for c in color_bgr])
            upper = np.array([min(255, c + tolerance) for c in color_bgr])
            
            mask = cv2.inRange(image, lower, upper)
            
            # Знаходимо контури
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                logger.warning(f"No buttons found with color: {color_bgr}")
                return False, (0, 0)
            
            # Беремо найбільший контур (найімовірніше це кнопка)
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Центр кнопки
            center_x = x + w // 2
            center_y = y + h // 2
            
            logger.info(f"Button found at ({center_x}, {center_y})")
            return True, (center_x, center_y)
        
        except Exception as e:
            logger.error(f"Button finder by color error: {e}")
            return False, (0, 0)
    
    def find_and_click_button_by_color(self, color_bgr: tuple) -> str:
        """
        Знаходить кнопку за кольором та натискає на неї
        
        Args:
            color_bgr: Колір в форматі BGR
            
        Returns:
            str: Результат операції
        """
        try:
            logger.info(f"Finding and clicking button by color: {color_bgr}")
            
            found, (x, y) = self.find_button_by_color(color_bgr)
            
            if not found or (x == 0 and y == 0):
                return f"❌ Кнопка з кольором {color_bgr} не знайдена"
            
            # Натискаємо на кнопку
            self.click.click(x, y)
            
            logger.info(f"Button clicked by color at ({x}, {y})")
            return f"✅ Кнопка натиснута на ({x}, {y})"
        
        except Exception as e:
            logger.error(f"Click button by color error: {e}")
            return f"❌ Помилка: {str(e)}"
