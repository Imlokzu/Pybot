import logging
import pyautogui
from pc_control.keyboard import KeyboardController
from pc_control.click import ClickController
from pc_control.windows import WindowController

logger = logging.getLogger(__name__)

# Предефіновані шорткати
SHORTCUTS = {
    'fullscreen': {
        'description': 'Повноекранний режим',
        'action': 'alt_enter'
    },
    'copy': {
        'description': 'Копіювати (Ctrl+C)',
        'action': 'hotkey',
        'keys': ['ctrl', 'c']
    },
    'paste': {
        'description': 'Вставити (Ctrl+V)',
        'action': 'hotkey',
        'keys': ['ctrl', 'v']
    },
    'cut': {
        'description': 'Вирізати (Ctrl+X)',
        'action': 'hotkey',
        'keys': ['ctrl', 'x']
    },
    'undo': {
        'description': 'Скасувати (Ctrl+Z)',
        'action': 'hotkey',
        'keys': ['ctrl', 'z']
    },
    'redo': {
        'description': 'Повторити (Ctrl+Y)',
        'action': 'hotkey',
        'keys': ['ctrl', 'y']
    },
    'save': {
        'description': 'Зберегти (Ctrl+S)',
        'action': 'hotkey',
        'keys': ['ctrl', 's']
    },
    'select_all': {
        'description': 'Виділити все (Ctrl+A)',
        'action': 'hotkey',
        'keys': ['ctrl', 'a']
    },
    'find': {
        'description': 'Пошук (Ctrl+F)',
        'action': 'hotkey',
        'keys': ['ctrl', 'f']
    },
    'replace': {
        'description': 'Замінити (Ctrl+H)',
        'action': 'hotkey',
        'keys': ['ctrl', 'h']
    },
    'new_tab': {
        'description': 'Нова вкладка (Ctrl+T)',
        'action': 'hotkey',
        'keys': ['ctrl', 't']
    },
    'close_tab': {
        'description': 'Закрити вкладку (Ctrl+W)',
        'action': 'hotkey',
        'keys': ['ctrl', 'w']
    },
    'switch_window': {
        'description': 'Перемикання вікон (Alt+Tab)',
        'action': 'hotkey',
        'keys': ['alt', 'tab']
    },
    'task_manager': {
        'description': 'Диспетчер завдань (Ctrl+Shift+Esc)',
        'action': 'hotkey',
        'keys': ['ctrl', 'shift', 'esc']
    },
    'delete': {
        'description': 'Видалити (Delete)',
        'action': 'key',
        'key': 'delete'
    },
    'backspace': {
        'description': 'Видалити назад (Backspace)',
        'action': 'key',
        'key': 'backspace'
    },
    'enter': {
        'description': 'Enter',
        'action': 'key',
        'key': 'enter'
    },
    'space': {
        'description': 'Пробіл (Space)',
        'action': 'key',
        'key': 'space'
    },
    'tab': {
        'description': 'Tab',
        'action': 'key',
        'key': 'tab'
    },
    'escape': {
        'description': 'Escape',
        'action': 'key',
        'key': 'escape'
    },
    'screenshot': {
        'description': 'Скріншот (Print Screen)',
        'action': 'key',
        'key': 'printscreen'
    },
    # Mouse movement shortcuts
    'mouse_up': {
        'description': 'Рух миші вгору на 50px',
        'action': 'mouse_move',
        'direction': 'up',
        'distance': 50
    },
    'mouse_down': {
        'description': 'Рух миші вниз на 50px',
        'action': 'mouse_move',
        'direction': 'down',
        'distance': 50
    },
    'mouse_left': {
        'description': 'Рух миші вліво на 50px',
        'action': 'mouse_move',
        'direction': 'left',
        'distance': 50
    },
    'mouse_right': {
        'description': 'Рух миші вправо на 50px',
        'action': 'mouse_move',
        'direction': 'right',
        'distance': 50
    },
    'mouse_up_small': {
        'description': 'Рух миші вгору на 10px',
        'action': 'mouse_move',
        'direction': 'up',
        'distance': 10
    },
    'mouse_down_small': {
        'description': 'Рух миші вниз на 10px',
        'action': 'mouse_move',
        'direction': 'down',
        'distance': 10
    },
    'mouse_left_small': {
        'description': 'Рух миші вліво на 10px',
        'action': 'mouse_move',
        'direction': 'left',
        'distance': 10
    },
    'mouse_right_small': {
        'description': 'Рух миші вправо на 10px',
        'action': 'mouse_move',
        'direction': 'right',
        'distance': 10
    },
    'mouse_center': {
        'description': 'Рух миші в центр екрану',
        'action': 'mouse_center'
    },
    'mouse_click': {
        'description': 'Клік лівою кнопкою миші',
        'action': 'mouse_click',
        'button': 'left'
    },
    'mouse_right_click': {
        'description': 'Клік правою кнопкою миші',
        'action': 'mouse_click',
        'button': 'right'
    },
    'mouse_double_click': {
        'description': 'Подвійний клік миші',
        'action': 'mouse_double_click'
    },
}


class ShortcutExecutor:
    """Виконавець шорткатів"""
    
    def __init__(self):
        self.keyboard = KeyboardController()
        self.click = ClickController()
        self.windows = WindowController()
    
    def get_shortcuts(self) -> dict:
        """Отримує список всіх шорткатів"""
        return SHORTCUTS
    
    def get_shortcut_list(self) -> str:
        """Повертає форматований список шорткатів"""
        text = "📋 Доступні шорткати:\n\n"
        for name, info in SHORTCUTS.items():
            text += f"• {name} - {info['description']}\n"
        text += "\n💡 Ви також можете використовувати користувацькі комбінації:\n"
        text += "/shortcut alt+f4\n"
        text += "/shortcut ctrl+alt+delete\n"
        text += "/shortcut shift+tab"
        return text
    
    def parse_custom_shortcut(self, shortcut_str: str) -> tuple[bool, list]:
        """
        Розпарсовує користувацький шорткат
        
        Args:
            shortcut_str: Строка типу "alt+f4" або "ctrl+alt+delete"
            
        Returns:
            (успіх, список клавіш)
        """
        try:
            # Видаляємо пробіли
            shortcut_str = shortcut_str.strip().lower()
            
            # Розділяємо по +
            keys = shortcut_str.split('+')
            
            # Перевіряємо, що всі клавіші валідні
            valid_keys = {
                'ctrl', 'alt', 'shift', 'enter', 'tab', 'escape',
                'delete', 'backspace', 'space', 'f1', 'f2', 'f3', 'f4',
                'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
                'home', 'end', 'pageup', 'pagedown', 'insert',
                'up', 'down', 'left', 'right', 'printscreen'
            }
            
            for key in keys:
                if key not in valid_keys:
                    return False, []
            
            return True, keys
        
        except Exception as e:
            logger.error(f"Error parsing custom shortcut: {e}")
            return False, []
    
    async def execute_shortcut(self, shortcut_name: str) -> str:
        """
        Виконує шорткат за назвою або користувацьку комбінацію
        
        Args:
            shortcut_name: Назва шорткату або комбінація (alt+f4)
            
        Returns:
            str: Результат виконання
        """
        try:
            shortcut_name = shortcut_name.lower().strip()
            
            # Спочатку перевіряємо, чи це предефінований шорткат
            if shortcut_name in SHORTCUTS:
                shortcut = SHORTCUTS[shortcut_name]
                action = shortcut.get('action')
                description = shortcut.get('description')
                
                logger.info(f"Executing predefined shortcut: {shortcut_name}")
                
                if action == 'alt_enter':
                    self.keyboard.alt_enter()
                    return f"✅ {description} виконано"
                
                elif action == 'hotkey':
                    keys = shortcut.get('keys', [])
                    self.keyboard.hotkey(*keys)
                    return f"✅ {description} виконано"
                
                elif action == 'key':
                    key = shortcut.get('key')
                    self.keyboard.press_key(key)
                    return f"✅ {description} виконано"
                
                elif action == 'mouse_move':
                    return self._execute_mouse_move(shortcut)
                
                elif action == 'mouse_center':
                    return self._execute_mouse_center()
                
                elif action == 'mouse_click':
                    button = shortcut.get('button', 'left')
                    current_pos = pyautogui.position()
                    if self.click.click(current_pos.x, current_pos.y, button=button):
                        return f"✅ {description} виконано"
                    else:
                        return f"❌ Помилка кліку миші"
                
                elif action == 'mouse_double_click':
                    current_pos = pyautogui.position()
                    if self.click.double_click(current_pos.x, current_pos.y):
                        return f"✅ {description} виконано"
                    else:
                        return f"❌ Помилка подвійного кліку миші"
                
                else:
                    return f"❌ Невідомий тип дії: {action}"
            
            # Якщо не знайдено - спробуємо розпарсити як користувацьку комбінацію
            elif '+' in shortcut_name:
                is_valid, keys = self.parse_custom_shortcut(shortcut_name)
                
                if not is_valid or not keys:
                    return f"❌ Невалідна комбінація: '{shortcut_name}'\n\nДозволені клавіші: ctrl, alt, shift, enter, tab, escape, delete, backspace, space, f1-f12, home, end, pageup, pagedown, insert, стрілки, printscreen"
                
                logger.info(f"Executing custom shortcut: {shortcut_name}")
                self.keyboard.hotkey(*keys)
                return f"✅ Комбінація {shortcut_name.upper()} виконана"
            
            else:
                return f"❌ Шорткат '{shortcut_name}' не знайдено!\n\n{self.get_shortcut_list()}"
        
        except Exception as e:
            logger.error(f"Shortcut execution error: {e}")
            return f"❌ Помилка виконання шорткату: {str(e)}"
    
    def _execute_mouse_move(self, shortcut: dict) -> str:
        """Виконує рух миші"""
        try:
            direction = shortcut.get('direction')
            distance = shortcut.get('distance', 50)
            description = shortcut.get('description', '')
            
            current_x, current_y = pyautogui.position()
            
            if direction == 'up':
                new_x, new_y = current_x, current_y - distance
            elif direction == 'down':
                new_x, new_y = current_x, current_y + distance
            elif direction == 'left':
                new_x, new_y = current_x - distance, current_y
            elif direction == 'right':
                new_x, new_y = current_x + distance, current_y
            else:
                return f"❌ Невідомий напрямок: {direction}"
            
            if self.click.move_mouse(new_x, new_y):
                return f"✅ {description} виконано"
            else:
                return f"❌ Помилка руху миші"
                
        except Exception as e:
            logger.error(f"Mouse move error: {e}")
            return f"❌ Помилка руху миші: {str(e)}"
    
    def _execute_mouse_center(self) -> str:
        """Виконує рух миші в центр екрану"""
        try:
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2
            
            if self.click.move_mouse(center_x, center_y):
                return f"✅ Рух миші в центр екрану виконано"
            else:
                return f"❌ Помилка руху миші в центр"
                
        except Exception as e:
            logger.error(f"Mouse center error: {e}")
            return f"❌ Помилка руху миші в центр: {str(e)}"
