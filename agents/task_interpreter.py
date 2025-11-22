import logging
import json
import re

logger = logging.getLogger(__name__)


class TaskInterpreter:
    """Локальний парсер завдань (без API)"""
    
    def __init__(self):
        self.keywords = {
            'click': ['клік', 'натисни', 'нажми', 'click', 'press'],
            'type': ['напиши', 'введи', 'набери', 'type', 'write'],
            'screenshot': ['скріншот', 'фото', 'screenshot', 'screen'],
            'open_app': ['відкрий', 'запусти', 'open', 'start', 'launch'],
            'close_app': ['закрий', 'вимкни', 'close', 'exit'],
            'alt_enter': ['alt enter', 'alt+enter'],
            'enter_alt': ['enter alt', 'enter+alt'],
            'hotkey': ['ctrl', 'shift', 'tab', 'escape'],
            'wait': ['чекай', 'зачекай', 'wait', 'pause'],
            'drag': ['перетягни', 'drag', 'move'],
        }
    
    async def interpret(self, task_text: str) -> dict:
        """Розпарсує завдання без API"""
        try:
            task_lower = task_text.lower()
            
            # Визначаємо дію
            action = self._detect_action(task_lower)
            target = self._extract_target(task_text, action)
            parameters = self._extract_parameters(task_text, action)
            
            result = {
                "action": action,
                "target": target,
                "parameters": parameters,
                "description": task_text
            }
            
            logger.info(f"Task interpreted: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Task interpretation error: {e}")
            return {
                "action": "unknown",
                "target": task_text,
                "parameters": {},
                "description": task_text
            }
    
    def _detect_action(self, task_lower: str) -> str:
        """Визначає тип дії"""
        for action, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    return action
        
        # Якщо не розпізнано - за замовчуванням "type" (введення тексту)
        # Це найпоширеніша дія
        return "type"
    
    def _extract_target(self, task_text: str, action: str) -> str:
        """Витягує мету дії"""
        task_lower = task_text.lower()
        
        if action == 'type':
            # Шукаємо текст у лапках
            match = re.search(r'["\']([^"\']+)["\']', task_text)
            if match:
                return match.group(1)
            # Або текст після "напиши"
            words = task_text.split()
            for i, word in enumerate(words):
                if word.lower() in ['напиши', 'введи', 'набери', 'type', 'write']:
                    return ' '.join(words[i+1:])
        
        elif action == 'click':
            # Шукаємо назву кнопки/елемента
            match = re.search(r'на\s+([а-яА-Я\w]+)', task_text)
            if match:
                return match.group(1)
        
        elif action == 'open_app':
            # Шукаємо назву додатку
            match = re.search(r'(notepad|calc|chrome|firefox|explorer|word|excel)', task_lower)
            if match:
                return match.group(1)
        
        return task_text
    
    def _extract_parameters(self, task_text: str, action: str) -> dict:
        """Витягує параметри дії"""
        params = {}
        
        if action == 'click':
            # Шукаємо координати
            match = re.search(r'(\d+)\s*,\s*(\d+)', task_text)
            if match:
                params['x'] = int(match.group(1))
                params['y'] = int(match.group(2))
            
            # Тип кліку
            if 'подвійний' in task_text.lower() or 'double' in task_text.lower():
                params['double'] = True
            if 'право' in task_text.lower() or 'right' in task_text.lower():
                params['button'] = 'right'
        
        elif action == 'wait':
            # Шукаємо час очікування
            match = re.search(r'(\d+)\s*(сек|секунд|sec|second)', task_text)
            if match:
                params['seconds'] = int(match.group(1))
            else:
                params['seconds'] = 1
        
        elif action == 'hotkey':
            # Шукаємо комбінацію клавіш
            if 'ctrl' in task_text.lower():
                params['keys'] = ['ctrl']
            if 'alt' in task_text.lower():
                params['keys'] = params.get('keys', []) + ['alt']
            if 'shift' in task_text.lower():
                params['keys'] = params.get('keys', []) + ['shift']
        
        return params
