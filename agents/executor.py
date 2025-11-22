import logging
import asyncio
import time
from pc_control.click import ClickController
from pc_control.keyboard import KeyboardController
from pc_control.screen import ScreenCapture
from pc_control.windows import WindowController

logger = logging.getLogger(__name__)


class Executor:
    """Виконавець команд (імітування дій людини)"""
    
    def __init__(self):
        self.click = ClickController()
        self.keyboard = KeyboardController()
        self.screen = ScreenCapture()
        self.windows = WindowController()
    
    async def prepare_commands(self, task: dict) -> str:
        """Готує команди для виконання"""
        try:
            action = task.get('action', 'unknown')
            target = task.get('target', '')
            description = task.get('description', '')
            
            if action == 'click':
                return f"🖱️ Клік по: {target}\n📝 {description}"
            elif action == 'type':
                return f"⌨️ Набрати текст: {target}\n📝 {description}"
            elif action == 'screenshot':
                return f"📸 Зробити скріншот\n📝 {description}"
            elif action == 'open_app':
                return f"🚀 Відкрити: {target}\n📝 {description}"
            elif action == 'close_app':
                return f"❌ Закрити: {target}\n📝 {description}"
            elif action == 'hotkey':
                return f"⌨️ Комбінація: {target}\n📝 {description}"
            elif action == 'wait':
                return f"⏳ Чекаю: {target}\n📝 {description}"
            elif action == 'drag':
                return f"🖱️ Перетягування: {target}\n📝 {description}"
            elif action == 'alt_enter':
                return f"⌨️ Alt+Enter\n📝 {description}"
            elif action == 'enter_alt':
                return f"⌨️ Enter+Alt\n📝 {description}"
            else:
                return f"❓ Дія: {action}\n📝 {description}"
            
        except Exception as e:
            logger.error(f"Command preparation error: {e}")
            return f"❌ Помилка: {str(e)}"
    
    async def execute(self, task: dict) -> str:
        """Виконує завдання"""
        try:
            action = task.get('action', 'unknown')
            target = task.get('target', '')
            parameters = task.get('parameters', {})
            
            logger.info(f"Executing action: {action}, target: {target}")
            
            if action == 'click':
                return await self._execute_click(target, parameters)
            
            elif action == 'type':
                return await self._execute_type(target, parameters)
            
            elif action == 'screenshot':
                return await self._execute_screenshot()
            
            elif action == 'open_app':
                return await self._execute_open_app(target)
            
            elif action == 'close_app':
                return await self._execute_close_app(target)
            
            elif action == 'hotkey':
                return await self._execute_hotkey(parameters)
            
            elif action == 'wait':
                return await self._execute_wait(parameters)
            
            elif action == 'drag':
                return await self._execute_drag(parameters)
            
            elif action == 'alt_enter':
                return await self._execute_alt_enter()
            
            elif action == 'enter_alt':
                return await self._execute_enter_alt()
            
            else:
                return f"❓ Невідома дія: {action}"
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"❌ Помилка виконання: {str(e)}"
    
    async def _execute_click(self, target: str, params: dict) -> str:
        """Виконує клік"""
        try:
            x = params.get('x')
            y = params.get('y')
            
            if x and y:
                # Клік по координатам
                if params.get('double'):
                    self.click.double_click(x, y)
                    return f"✅ Подвійний клік по ({x}, {y})"
                elif params.get('button') == 'right':
                    self.click.right_click(x, y)
                    return f"✅ Правий клік по ({x}, {y})"
                else:
                    self.click.click(x, y)
                    return f"✅ Клік по ({x}, {y})"
            else:
                # Пошук по тексту на екрані
                coords = self.screen.find_text_on_screen(target)
                if coords:
                    self.click.click(coords[0], coords[1])
                    return f"✅ Клік по '{target}' на {coords}"
                else:
                    return f"⚠️ Не знайдено '{target}' на екрані"
        
        except Exception as e:
            logger.error(f"Click execution error: {e}")
            return f"❌ Помилка кліку: {str(e)}"
    
    async def _execute_type(self, text: str, params: dict) -> str:
        """Виконує введення тексту"""
        try:
            # Спробуємо Unicode (для українського)
            self.keyboard.write_unicode(text)
            # Натискаємо Enter після введення
            await asyncio.sleep(0.2)
            self.keyboard.press_key('enter')
            return f"✅ Текст введено: '{text}' + Enter"
        except Exception as e:
            logger.error(f"Type execution error: {e}")
            return f"❌ Помилка введення: {str(e)}"
    
    async def _execute_screenshot(self) -> str:
        """Робить скріншот"""
        try:
            path = self.screen.capture()
            return f"✅ Скріншот збережено: {path}"
        except Exception as e:
            logger.error(f"Screenshot execution error: {e}")
            return f"❌ Помилка скріншота: {str(e)}"
    
    async def _execute_open_app(self, app_name: str) -> str:
        """Відкриває додаток"""
        try:
            app_paths = {
                'notepad': 'notepad.exe',
                'calc': 'calc.exe',
                'explorer': 'explorer.exe',
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'word': 'winword.exe',
                'excel': 'excel.exe',
            }
            
            app_path = app_paths.get(app_name.lower(), app_name)
            self.windows.open_app(app_path)
            await asyncio.sleep(2)
            return f"✅ Додаток '{app_name}' відкрито"
        except Exception as e:
            logger.error(f"Open app execution error: {e}")
            return f"❌ Помилка відкриття: {str(e)}"
    
    async def _execute_close_app(self, app_name: str) -> str:
        """Закриває додаток"""
        try:
            self.windows.close_app(app_name)
            return f"✅ Додаток '{app_name}' закрито"
        except Exception as e:
            logger.error(f"Close app execution error: {e}")
            return f"❌ Помилка закриття: {str(e)}"
    
    async def _execute_hotkey(self, params: dict) -> str:
        """Виконує комбінацію клавіш"""
        try:
            keys = params.get('keys', [])
            if keys:
                self.keyboard.hotkey(*keys)
                return f"✅ Комбінація {'+'.join(keys)} виконана"
            return "⚠️ Немає клавіш для виконання"
        except Exception as e:
            logger.error(f"Hotkey execution error: {e}")
            return f"❌ Помилка комбінації: {str(e)}"
    
    async def _execute_wait(self, params: dict) -> str:
        """Чекає певний час"""
        try:
            seconds = params.get('seconds', 1)
            await asyncio.sleep(seconds)
            return f"✅ Очікування {seconds} сек завершено"
        except Exception as e:
            logger.error(f"Wait execution error: {e}")
            return f"❌ Помилка очікування: {str(e)}"
    
    async def _execute_drag(self, params: dict) -> str:
        """Перетягує мишу"""
        try:
            x1 = params.get('x1')
            y1 = params.get('y1')
            x2 = params.get('x2')
            y2 = params.get('y2')
            
            if all([x1, y1, x2, y2]):
                self.click.drag(x1, y1, x2, y2)
                return f"✅ Перетягування з ({x1}, {y1}) на ({x2}, {y2})"
            return "⚠️ Недостатньо координат"
        except Exception as e:
            logger.error(f"Drag execution error: {e}")
            return f"❌ Помилка перетягування: {str(e)}"
    
    async def _execute_alt_enter(self) -> str:
        """Виконує Alt+Enter"""
        try:
            self.keyboard.alt_enter()
            return f"✅ Alt+Enter виконано"
        except Exception as e:
            logger.error(f"Alt+Enter execution error: {e}")
            return f"❌ Помилка Alt+Enter: {str(e)}"
    
    async def _execute_enter_alt(self) -> str:
        """Виконує Enter+Alt"""
        try:
            self.keyboard.enter_alt()
            return f"✅ Enter+Alt виконано"
        except Exception as e:
            logger.error(f"Enter+Alt execution error: {e}")
            return f"❌ Помилка Enter+Alt: {str(e)}"
