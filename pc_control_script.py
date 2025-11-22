#!/usr/bin/env python3
"""
Скрипт контролю ПК
Імітує дії людини: клік, клавіатура, скріншоти
"""

import asyncio
import sys
from pc_control.click import ClickController
from pc_control.keyboard import KeyboardController
from pc_control.screen import ScreenCapture
from pc_control.windows import WindowController


class PCController:
    """Головний контролер ПК"""
    
    def __init__(self):
        self.click = ClickController()
        self.keyboard = KeyboardController()
        self.screen = ScreenCapture()
        self.windows = WindowController()
    
    def screenshot(self):
        """Зробити скріншот"""
        print("📸 Беру скріншот...")
        path = self.screen.capture()
        print(f"✅ Скріншот збережено: {path}")
        return path
    
    def click(self, x: int, y: int, button: str = 'left', double: bool = False):
        """Клік по координатам"""
        print(f"🖱️ Клік по ({x}, {y})")
        if double:
            self.click.double_click(x, y)
            print("✅ Подвійний клік виконано")
        elif button == 'right':
            self.click.right_click(x, y)
            print("✅ Правий клік виконано")
        else:
            self.click.click(x, y)
            print("✅ Клік виконано")
    
    def type_text(self, text: str):
        """Набрати текст"""
        print(f"⌨️ Набираю: {text}")
        self.keyboard.write_unicode(text)
        print("✅ Текст введено")
    
    def press_key(self, key: str):
        """Натиснути клавішу"""
        print(f"⌨️ Натискаю: {key}")
        self.keyboard.press_key(key)
        print("✅ Клавіша натиснута")
    
    def hotkey(self, *keys):
        """Комбінація клавіш"""
        print(f"⌨️ Комбінація: {'+'.join(keys)}")
        self.keyboard.hotkey(*keys)
        print("✅ Комбінація виконана")
    
    def open_app(self, app_name: str):
        """Відкрити додаток"""
        print(f"🚀 Відкриваю: {app_name}")
        self.windows.open_app(app_name)
        print("✅ Додаток відкрито")
    
    def close_app(self, app_name: str):
        """Закрити додаток"""
        print(f"❌ Закриваю: {app_name}")
        self.windows.close_app(app_name)
        print("✅ Додаток закрито")
    
    def find_text(self, text: str):
        """Знайти текст на екрані"""
        print(f"🔍 Шукаю текст: {text}")
        coords = self.screen.find_text_on_screen(text)
        if coords:
            print(f"✅ Знайдено на {coords}")
            return coords
        else:
            print(f"❌ Текст не знайдено")
            return None
    
    def wait(self, seconds: float):
        """Чекати"""
        print(f"⏳ Чекаю {seconds} сек...")
        import time
        time.sleep(seconds)
        print("✅ Очікування завершено")
    
    def drag(self, x1: int, y1: int, x2: int, y2: int):
        """Перетягування"""
        print(f"🖱️ Перетягую з ({x1}, {y1}) на ({x2}, {y2})")
        self.click.drag(x1, y1, x2, y2)
        print("✅ Перетягування виконано")


def print_menu():
    """Виводить меню"""
    print("\n" + "="*50)
    print("🖥️  PC CONTROL SCRIPT")
    print("="*50)
    print("\nКоманди:")
    print("1. screenshot         - Скріншот")
    print("2. click X Y          - Клік по (X, Y)")
    print("3. type TEXT          - Набрати текст")
    print("4. key KEY            - Натиснути клавішу")
    print("5. hotkey K1 K2 ...   - Комбінація клавіш")
    print("6. open APP           - Відкрити додаток")
    print("7. close APP          - Закрити додаток")
    print("8. find TEXT          - Знайти текст")
    print("9. wait SECONDS       - Чекати")
    print("10. drag X1 Y1 X2 Y2  - Перетягування")
    print("11. help              - Довідка")
    print("12. exit              - Вихід")
    print("="*50 + "\n")


def main():
    """Головна функція"""
    controller = PCController()
    
    print("\n🖥️  PC CONTROL SCRIPT - Інтерактивний режим\n")
    print("Введіть команду (або 'help' для довідки):\n")
    
    while True:
        try:
            command = input(">>> ").strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == 'help':
                print_menu()
            
            elif cmd == 'screenshot':
                controller.screenshot()
            
            elif cmd == 'click':
                if len(parts) < 3:
                    print("❌ Використовуйте: click X Y")
                    continue
                x, y = int(parts[1]), int(parts[2])
                double = 'double' in parts
                button = 'right' if 'right' in parts else 'left'
                controller.click(x, y, button, double)
            
            elif cmd == 'type':
                text = ' '.join(parts[1:])
                if not text:
                    print("❌ Введіть текст")
                    continue
                controller.type_text(text)
            
            elif cmd == 'key':
                if len(parts) < 2:
                    print("❌ Використовуйте: key KEY")
                    continue
                controller.press_key(parts[1])
            
            elif cmd == 'hotkey':
                if len(parts) < 2:
                    print("❌ Використовуйте: hotkey KEY1 KEY2 ...")
                    continue
                controller.hotkey(*parts[1:])
            
            elif cmd == 'open':
                if len(parts) < 2:
                    print("❌ Використовуйте: open APP")
                    continue
                controller.open_app(parts[1])
            
            elif cmd == 'close':
                if len(parts) < 2:
                    print("❌ Використовуйте: close APP")
                    continue
                controller.close_app(parts[1])
            
            elif cmd == 'find':
                text = ' '.join(parts[1:])
                if not text:
                    print("❌ Введіть текст для пошуку")
                    continue
                controller.find_text(text)
            
            elif cmd == 'wait':
                if len(parts) < 2:
                    print("❌ Використовуйте: wait SECONDS")
                    continue
                controller.wait(float(parts[1]))
            
            elif cmd == 'drag':
                if len(parts) < 5:
                    print("❌ Використовуйте: drag X1 Y1 X2 Y2")
                    continue
                x1, y1, x2, y2 = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                controller.drag(x1, y1, x2, y2)
            
            elif cmd == 'exit':
                print("👋 До побачення!")
                break
            
            else:
                print(f"❌ Невідома команда: {cmd}")
                print("Введіть 'help' для довідки")
        
        except ValueError as e:
            print(f"❌ Помилка: {e}")
        except KeyboardInterrupt:
            print("\n👋 До побачення!")
            break
        except Exception as e:
            print(f"❌ Помилка: {e}")


if __name__ == '__main__':
    main()
