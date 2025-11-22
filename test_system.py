#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки системи
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


async def test_imports():
    """Тест імпортів"""
    logger.info("🔍 Тестування імпортів...")
    try:
        from agents.task_interpreter import TaskInterpreter
        from agents.executor import Executor
        from agents.approval import ApprovalAgent
        from pc_control.screen import ScreenCapture
        from pc_control.click import ClickController
        from pc_control.keyboard import KeyboardController
        from pc_control.windows import WindowController
        logger.info("✅ Всі імпорти успішні!")
        return True
    except Exception as e:
        logger.error(f"❌ Помилка імпорту: {e}")
        return False


async def test_env():
    """Тест конфігу"""
    logger.info("🔍 Тестування конфігу...")
    
    token = os.getenv('TELEGRAM_TOKEN')
    admin_id = os.getenv('ADMIN_ID')
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not token or token == 'YOUR_BOT_TOKEN_HERE':
        logger.warning("⚠️  TELEGRAM_TOKEN не встановлений")
    else:
        logger.info("✅ TELEGRAM_TOKEN встановлений")
    
    if not admin_id or admin_id == 'YOUR_TELEGRAM_ID_HERE':
        logger.warning("⚠️  ADMIN_ID не встановлений")
    else:
        logger.info("✅ ADMIN_ID встановлений")
    
    if not api_key or api_key == 'sk-your-key-here':
        logger.warning("⚠️  OPENAI_API_KEY не встановлений (опціонально)")
    else:
        logger.info("✅ OPENAI_API_KEY встановлений")
    
    return bool(token and admin_id)


async def test_agents():
    """Тест агентів"""
    logger.info("🔍 Тестування агентів...")
    try:
        from agents.task_interpreter import TaskInterpreter
        from agents.executor import Executor
        
        interpreter = TaskInterpreter()
        executor = Executor()
        
        # Тест Task Interpreter
        task = await interpreter.interpret("відкрити браузер")
        logger.info(f"✅ Task Interpreter: {task}")
        
        # Тест Executor
        commands = await executor.prepare_commands(task)
        logger.info(f"✅ Executor: {commands}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Помилка агентів: {e}")
        return False


async def test_pc_control():
    """Тест PC Control"""
    logger.info("🔍 Тестування PC Control...")
    try:
        from pc_control.screen import ScreenCapture
        from pc_control.click import ClickController
        from pc_control.keyboard import KeyboardController
        from pc_control.windows import WindowController
        
        screen = ScreenCapture()
        click = ClickController()
        keyboard = KeyboardController()
        windows = WindowController()
        
        logger.info("✅ ScreenCapture: OK")
        logger.info("✅ ClickController: OK")
        logger.info("✅ KeyboardController: OK")
        logger.info("✅ WindowController: OK")
        
        return True
    except Exception as e:
        logger.error(f"❌ Помилка PC Control: {e}")
        return False


async def main():
    """Головна функція тестування"""
    logger.info("=" * 50)
    logger.info("🤖 ТЕСТУВАННЯ СИСТЕМИ")
    logger.info("=" * 50)
    
    results = {
        "Імпорти": await test_imports(),
        "Конфіг": await test_env(),
        "Агенти": await test_agents(),
        "PC Control": await test_pc_control(),
    }
    
    logger.info("=" * 50)
    logger.info("📊 РЕЗУЛЬТАТИ:")
    logger.info("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    logger.info("=" * 50)
    if all_passed:
        logger.info("✅ ВСІ ТЕСТИ ПРОЙДЕНІ!")
        logger.info("🚀 Система готова до запуску: python main.py")
    else:
        logger.warning("⚠️  Деякі тести не пройшли")
        logger.warning("📝 Перевірте конфіг та залежності")
    logger.info("=" * 50)


if __name__ == '__main__':
    asyncio.run(main())
