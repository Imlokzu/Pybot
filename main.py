import asyncio
import logging
import os
import json
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from agents.task_interpreter import TaskInterpreter
from agents.gemini_interpreter import GeminiTaskInterpreter
from agents.executor import Executor
from agents.approval import ApprovalAgent
from pc_control.screen import ScreenCapture
from auth import AuthManager
from persistence import save_task, write_to_windsurf
from shortcuts import ShortcutExecutor
from windsurf_sync import (
    save_windsurf_change, get_pending_changes, accept_change, 
    reject_change, get_changes_list, get_accepted_changes, get_next_change_id
)
from button_finder import ButtonFinder
from mini_app_server import start_mini_app_server, stop_mini_app_server

load_dotenv()

# FSM States для /task
class TaskStates(StatesGroup):
    waiting_for_task = State()

# Логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ініціалізація
TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID')) if os.getenv('ADMIN_ID') else 0

if not TOKEN or TOKEN == 'YOUR_BOT_TOKEN_HERE':
    logger.error("❌ TELEGRAM_TOKEN не встановлений в .env")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Агенти
task_interpreter = GeminiTaskInterpreter()  # Using AI-powered interpreter
executor = Executor()
approval_agent = ApprovalAgent()
screen = ScreenCapture()
auth_manager = AuthManager()
shortcut_executor = ShortcutExecutor()
button_finder = ButtonFinder()

# Стан системи
system_state = {
    'waiting_approval': False,
    'pending_task': None,
    'task_id': None
}


@dp.message(Command('register'))
async def cmd_register(message: Message):
    """Реєстрація користувача"""
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    
    # Отримуємо пароль з команди
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❌ Використовуйте: /register <пароль>\n\n"
            "Приклад: /register Ml120998"
        )
        return
    
    password = args[1]
    
    # Реєструємо користувача
    success, msg = auth_manager.register_user(user_id, username, password)
    
    if success:
        await message.answer(msg)
        logger.info(f"User {user_id} registered successfully")
    else:
        await message.answer(msg)
        logger.warning(f"Registration failed for user {user_id}")


@dp.message(Command('login'))
async def cmd_login(message: Message):
    """Вхід в систему"""
    user_id = message.from_user.id
    
    # Перевіряємо, чи користувач вже аутентифікований
    if auth_manager.is_authenticated(user_id):
        username = auth_manager.get_username(user_id)
        await message.answer(f"✅ Ви вже аутентифіковані як '{username}'!")
        return
    
    # Отримуємо пароль з команди
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❌ Використовуйте: /login <пароль>\n\n"
            "Приклад: /login Ml120998"
        )
        return
    
    password = args[1]
    
    # Аутентифікуємо користувача
    success, msg = auth_manager.authenticate_user(user_id, password)
    
    if success:
        await message.answer(msg)
        logger.info(f"User {user_id} authenticated successfully")
    else:
        await message.answer(msg)
        logger.warning(f"Authentication failed for user {user_id}")


@dp.message(TaskStates.waiting_for_task)
async def process_task_input(message: Message, state: FSMContext):
    """Обробляє введене завдання без команди"""
    user_id = message.from_user.id
    task_text = message.text.strip()
    
    # Очищуємо стан
    await state.clear()
    
    try:
        await message.answer("🔄 Аналізую завдання...")
        
        # Task Interpreter агент розпарсює завдання
        parsed_task = await task_interpreter.interpret(task_text)
        logger.info(f"Task interpreted: {parsed_task}")
        
        # Executor агент готує команди
        commands = await executor.prepare_commands(parsed_task)
        logger.info(f"Commands prepared: {commands}")
        
        # Зберігаємо завдання
        save_task(user_id, task_text, "pending")
        write_to_windsurf(task_text, user_id)
        
        # Approval агент просить підтвердження
        system_state['pending_task'] = parsed_task
        system_state['pending_task_description'] = commands
        system_state['waiting_approval'] = True
        system_state['task_id'] = message.message_id
        
        approval_text = f"✅ Готово до виконання:\n\n{commands}\n\nПідтвердити?"
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Так", callback_data="approve_yes"),
                types.InlineKeyboardButton(text="❌ Ні", callback_data="approve_no")
            ]
        ])
        
        await message.answer(approval_text, reply_markup=keyboard)
        
    except Exception as e:
        await message.answer(f"❌ Помилка обробки: {str(e)}")
        logger.error(f"Task processing error: {e}")


@dp.message(Command('shortcut'))
async def cmd_shortcut(message: Message):
    """Виконати шорткат"""
    user_id = message.from_user.id
    
    # Перевіряємо аутентифікацію
    if not auth_manager.is_authenticated(user_id):
        await message.answer("🔐 Ви не аутентифіковані! Використовуйте /register або /login")
        return
    
    shortcut_name = message.text.replace('/shortcut ', '', 1).strip()
    
    if not shortcut_name:
        # Показуємо список шорткатів
        await message.answer(shortcut_executor.get_shortcut_list())
        return
    
    try:
        result = await shortcut_executor.execute_shortcut(shortcut_name)
        await message.answer(result)
        logger.info(f"Shortcut executed: {shortcut_name}")
    except Exception as e:
        await message.answer(f"❌ Помилка: {str(e)}")
        logger.error(f"Shortcut error: {e}")


@dp.message(Command('logout'))
async def cmd_logout(message: Message):
    """Вихід з системи"""
    user_id = message.from_user.id
    success, msg = auth_manager.logout_user(user_id)
    await message.answer(msg)


@dp.message(Command('start'))
async def cmd_start(message: Message):
    """Стартова команда"""
    user_id = message.from_user.id
    
    # Перевіряємо, чи користувач аутентифікований
    if not auth_manager.is_authenticated(user_id):
        await message.answer(
            "🔐 Ви не аутентифіковані!\n\n"
            "Спочатку зареєструйтеся:\n"
            "/register <пароль>\n\n"
            "Або увійдіть:\n"
            "/login <пароль>\n\n"
            "Приклад: /register Ml120998"
        )
        return
    
    username = auth_manager.get_username(user_id)
    
    # Отримуємо реальне ім'я користувача з Telegram
    user_first_name = message.from_user.first_name or "Користувач"
    user_last_name = message.from_user.last_name or ""
    real_name = f"{user_first_name} {user_last_name}".strip()
    
    # Меню з кнопками - новий дизайн
    from aiogram.types import WebAppInfo
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎮 PC Control Mini App",
                web_app=WebAppInfo(url="https://transcendent-starburst-51e9ab.netlify.app/")
            )
        ],
        [
            InlineKeyboardButton(text="📸 Скріншот", callback_data="menu_screenshot"),
            InlineKeyboardButton(text="📋 Зміни", callback_data="menu_changes")
        ],
        [
            InlineKeyboardButton(text="✏️ Завдання", callback_data="menu_task"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="menu_settings")
        ],
        [
            InlineKeyboardButton(text="📊 Статус", callback_data="menu_status"),
            InlineKeyboardButton(text="❓ Допомога", callback_data="menu_help")
        ],
        [
            InlineKeyboardButton(text="🚪 Вихід", callback_data="menu_logout")
        ]
    ])
    
    welcome_text = (
        "╔════════════════════════════════╗\n"
        "║  🤖 PC CONTROL BOT 🤖  ║\n"
        "╚════════════════════════════════╝\n\n"
        f"👋 <b>Привіт, {real_name}!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>📱 Головне меню</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Виберіть дію з меню нижче:\n\n"
        "✨ <i>Керуйте своїм ПК прямо з Telegram!</i>"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    logger.info(f"Bot started by user {user_id} ({username})")


@dp.message(Command('screenshot'))
async def cmd_screenshot(message: Message):
    """Отримати скріншот"""
    user_id = message.from_user.id
    
    # Перевіряємо аутентифікацію
    if not auth_manager.is_authenticated(user_id):
        await message.answer("🔐 Ви не аутентифіковані! Використовуйте /register або /login")
        return
    
    try:
        await message.answer("📸 Беру скріншот...")
        screenshot_path = screen.capture()
        
        # Використовуємо FSInputFile для відправки файлу
        photo = FSInputFile(screenshot_path)
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption="📸 Поточний стан екрану"
        )
        logger.info("Screenshot sent successfully")
    except Exception as e:
        await message.answer(f"❌ Помилка: {str(e)}")
        logger.error(f"Screenshot error: {e}")


@dp.message(Command('task'))
async def cmd_task(message: Message, state: FSMContext):
    """Отримати завдання від користувача"""
    user_id = message.from_user.id
    
    # Перевіряємо аутентифікацію
    if not auth_manager.is_authenticated(user_id):
        await message.answer("🔐 Ви не аутентифіковані! Використовуйте /register або /login")
        return
    
    task_text = message.text.replace('/task ', '', 1).strip()
    
    if not task_text:
        # Якщо просто /task - чекаємо на наступне повідомлення
        await state.set_state(TaskStates.waiting_for_task)
        await message.answer("📝 Введіть завдання:")
        return
    
    try:
        await message.answer("🔄 Аналізую завдання...")
        
        # Task Interpreter агент розпарсює завдання
        parsed_task = await task_interpreter.interpret(task_text)
        logger.info(f"Task interpreted: {parsed_task}")
        
        # Executor агент готує команди
        commands = await executor.prepare_commands(parsed_task)
        logger.info(f"Commands prepared: {commands}")
        
        # Зберігаємо завдання
        save_task(user_id, task_text, "pending")
        write_to_windsurf(task_text, user_id)
        
        # Approval агент просить підтвердження
        system_state['pending_task'] = parsed_task  # Зберігаємо словник, не строку
        system_state['pending_task_description'] = commands  # Зберігаємо опис для показу
        system_state['waiting_approval'] = True
        system_state['task_id'] = message.message_id
        
        approval_text = f"✅ Готово до виконання:\n\n{commands}\n\nПідтвердити?"
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Так", callback_data="approve_yes"),
                types.InlineKeyboardButton(text="❌ Ні", callback_data="approve_no")
            ]
        ])
        
        await message.answer(approval_text, reply_markup=keyboard)
        
    except Exception as e:
        await message.answer(f"❌ Помилка обробки: {str(e)}")
        logger.error(f"Task processing error: {e}")


@dp.callback_query(lambda c: c.data == "approve_yes")
async def approve_task(callback: types.CallbackQuery):
    """Підтвердження виконання завдання"""
    if ADMIN_ID and callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ заборонений", show_alert=True)
        return
    
    if not system_state['waiting_approval']:
        await callback.answer("❌ Немає очікуючих завдань", show_alert=True)
        return
    
    try:
        await callback.message.edit_text("⏳ Виконую завдання...")
        
        # Executor виконує завдання (словник)
        task = system_state['pending_task']
        result = await executor.execute(task)
        
        system_state['waiting_approval'] = False
        system_state['pending_task'] = None
        
        await callback.message.edit_text(
            f"✅ Завдання виконано!\n\n{result}",
            reply_markup=None
        )
        logger.info(f"Task executed successfully: {result}")
        
    except Exception as e:
        await callback.message.edit_text(f"❌ Помилка виконання: {str(e)}")
        logger.error(f"Task execution error: {e}")


@dp.callback_query(lambda c: c.data == "approve_no")
async def reject_task(callback: types.CallbackQuery):
    """Відхилення завдання"""
    if ADMIN_ID and callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ заборонений", show_alert=True)
        return
    
    system_state['waiting_approval'] = False
    system_state['pending_task'] = None
    
    await callback.message.edit_text("❌ Завдання скасовано", reply_markup=None)
    logger.info("Task rejected by user")


@dp.message(Command('status'))
async def cmd_status(message: Message):
    """Статус системи"""
    user_id = message.from_user.id
    
    # Перевіряємо аутентифікацію
    if not auth_manager.is_authenticated(user_id):
        await message.answer("🔐 Ви не аутентифіковані! Використовуйте /register або /login")
        return
    
    status_text = (
        "📊 Статус системи:\n\n"
        f"Bot: ✅ Online\n"
        f"Task Interpreter: ✅ Ready\n"
        f"Executor: ✅ Ready\n"
        f"Approval Agent: ✅ Ready\n"
        f"Waiting approval: {'🟡 Так' if system_state['waiting_approval'] else '🟢 Ні'}"
    )
    await message.answer(status_text)


@dp.message(Command('changes'))
async def cmd_changes(message: Message):
    """Показує очікуючі зміни з Windsurf"""
    user_id = message.from_user.id
    
    # Перевіряємо аутентифікацію
    if not auth_manager.is_authenticated(user_id):
        await message.answer("🔐 Ви не аутентифіковані! Використовуйте /register або /login")
        return
    
    changes_list = get_changes_list()
    if not changes_list:
        await message.answer("📋 Немає змін")
        return
    
    for change in changes_list:
        change_id = change.get('id', 'N/A')
        status = change.get('status', 'unknown')
        data = change.get('data', {})
        
        # Форматуємо інформацію про зміну
        file_name = data.get('file', 'unknown')
        change_desc = data.get('change', 'No description')
        line_num = data.get('line', 'N/A')
        
        status_emoji = "⏳" if status == "pending" else "✅" if status == "accepted" else "❌"
        
        text = f"{status_emoji} <b>Зміна: {change_id}</b>\n\n"
        text += f"📄 <b>Файл:</b> {file_name}\n"
        text += f"📝 <b>Опис:</b> {change_desc}\n"
        text += f"🔢 <b>Рядок:</b> {line_num}\n"
        text += f"📊 <b>Статус:</b> {status}\n"
        
        # Кнопки для управління змінами
        keyboard = None
        if status == "pending":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Прийняти", callback_data=f"accept_{change_id}"),
                    InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{change_id}")
                ]
            ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@dp.message(Command('accept'))
async def cmd_accept(message: Message):
    """Приймає зміну з Windsurf"""
    user_id = message.from_user.id
    
    # Перевіряємо аутентифікацію
    if not auth_manager.is_authenticated(user_id):
        await message.answer("🔐 Ви не аутентифіковані! Використовуйте /register або /login")
        return
    
    change_id = message.text.replace('/accept ', '', 1).strip()
    
    if not change_id:
        await message.answer("❌ Вкажіть ID змін. Приклад: /accept change_1")
        return
    
    try:
        success, msg = accept_change(change_id)
        await message.answer(msg)
        logger.info(f"Change accepted by user {user_id}: {change_id}")
    except Exception as e:
        await message.answer(f"❌ Помилка: {str(e)}")
        logger.error(f"Accept error: {e}")


@dp.message(Command('reject'))
async def cmd_reject(message: Message):
    """Відхиляє зміну з Windsurf"""
    user_id = message.from_user.id
    
    # Перевіряємо аутентифікацію
    if not auth_manager.is_authenticated(user_id):
        await message.answer("🔐 Ви не аутентифіковані! Використовуйте /register або /login")
        return
    
    change_id = message.text.replace('/reject ', '', 1).strip()
    
    if not change_id:
        await message.answer("❌ Вкажіть ID змін. Приклад: /reject change_1")
        return
    
    try:
        success, msg = reject_change(change_id)
        await message.answer(msg)
        logger.info(f"Change rejected by user {user_id}: {change_id}")
    except Exception as e:
        await message.answer(f"❌ Помилка: {str(e)}")
        logger.error(f"Reject error: {e}")


@dp.message(Command('click_button'))
async def cmd_click_button(message: Message):
    """Натискає на кнопку за текстом"""
    user_id = message.from_user.id
    
    # Перевіряємо аутентифікацію
    if not auth_manager.is_authenticated(user_id):
        await message.answer("🔐 Ви не аутентифіковані! Використовуйте /register або /login")
        return
    
    button_text = message.text.replace('/click_button ', '', 1).strip()
    
    if not button_text:
        await message.answer(
            "❌ Вкажіть текст кнопки.\n\n"
            "Приклади:\n"
            "/click_button Accept All\n"
            "/click_button OK\n"
            "/click_button Save"
        )
        return
    
    try:
        await message.answer(f"🔍 Шукаю кнопку '{button_text}'...")
        result = button_finder.find_and_click_button(button_text)
        await message.answer(result)
        logger.info(f"Button clicked by user {user_id}: {button_text}")
    except Exception as e:
        await message.answer(f"❌ Помилка: {str(e)}")
        logger.error(f"Click button error: {e}")


@dp.message(Command('help'))
async def cmd_help(message: Message):
    """Довідка"""
    help_text = (
        "🤖 PC Control Bot - Довідка\n\n"
        "Команди:\n"
        "/register - Реєстрація\n"
        "/login - Вхід\n"
        "/logout - Вихід\n"
        "/start - Запуск\n"
        "/screenshot - Скріншот\n"
        "/task - Виконати завдання\n"
        "/shortcut - Виконати шорткат\n"
        "/click_button - Натиснути кнопку\n"
        "/changes - Показати зміни з Windsurf\n"
        "/accept - Прийняти зміну\n"
        "/reject - Відхилити зміну\n"
        "/status - Статус\n"
        "/help - Ця довідка\n\n"
        "Приклади:\n"
        "/task напиши Hello\n"
        "/shortcut copy\n"
        "/click_button Accept All\n"
        "/changes\n"
        "/accept change_1"
    )
    await message.answer(help_text)


@dp.callback_query()
async def handle_callback(query: types.CallbackQuery):
    """Обробка всіх кнопок"""
    user_id = query.from_user.id
    
    # Перевіряємо аутентифікацію
    if not auth_manager.is_authenticated(user_id):
        await query.answer("🔐 Ви не аутентифіковані!", show_alert=True)
        return
    
    callback_data = query.data
    
    # Меню кнопки
    if callback_data == "menu_screenshot":
        await query.answer()
        screen = ScreenCapture()
        path = screen.capture()
        photo = FSInputFile(path)
        await query.message.answer_photo(
            photo,
            caption="📸 <b>Скріншот екрану</b>",
            parse_mode="HTML"
        )
    
    elif callback_data == "menu_changes":
        await query.answer()
        changes_list = get_changes_list()
        if not changes_list:
            no_changes_text = (
                "╔════════════════════════════════╗\n"
                "║  📋 ЗМІНИ  ║\n"
                "╚════════════════════════════════╝\n\n"
                "✨ <b>Немає змін для перегляду</b>\n\n"
                "💡 <i>Зміни з'являтимуться тут, коли будуть створені</i>"
            )
            await query.message.answer(no_changes_text, parse_mode="HTML")
            return
        
        header_text = (
            "╔════════════════════════════════╗\n"
            "║  📋 СПИСОК ЗМІН  ║\n"
            "╚════════════════════════════════╝\n\n"
            f"📊 <b>Всього змін: {len(changes_list)}</b>\n\n"
        )
        await query.message.answer(header_text, parse_mode="HTML")
        
        for idx, change in enumerate(changes_list, 1):
            change_id = change.get('id', 'N/A')
            status = change.get('status', 'unknown')
            data = change.get('data', {})
            
            file_name = data.get('file', 'unknown')
            change_desc = data.get('change', 'No description')
            line_num = data.get('line', 'N/A')
            
            status_emoji = "⏳" if status == "pending" else "✅" if status == "accepted" else "❌"
            status_text = "ОЧІКУЄ" if status == "pending" else "ПРИЙНЯТА" if status == "accepted" else "ВІДХИЛЕНА"
            
            text = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{status_emoji} <b>Зміна #{idx}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🆔 <b>ID:</b> <code>{change_id}</code>\n"
                f"📄 <b>Файл:</b> <code>{file_name}</code>\n"
                f"📝 <b>Опис:</b> {change_desc}\n"
                f"🔢 <b>Рядок:</b> <code>{line_num}</code>\n"
                f"📊 <b>Статус:</b> <code>{status_text}</code>\n"
            )
            
            keyboard = None
            if status == "pending":
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Прийняти", callback_data=f"accept_{change_id}"),
                        InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{change_id}")
                    ]
                ])
            
            await query.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    
    elif callback_data == "menu_task":
        await query.answer()
        task_text = (
            "╔════════════════════════════════╗\n"
            "║  ✏️ НОВЕ ЗАВДАННЯ  ║\n"
            "╚════════════════════════════════╝\n\n"
            "📝 <b>Введіть завдання для виконання:</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>📌 Приклади:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔤 <code>напиши Hello World</code>\n"
            "🖱️ <code>клікни на кнопку Сохранить</code>\n"
            "🚀 <code>відкрий Notepad</code>\n"
            "⌨️ <code>натисни Ctrl+C</code>\n\n"
            "💡 <i>Просто напишіть завдання природною мовою</i>"
        )
        await query.message.answer(task_text, parse_mode="HTML")
    
    elif callback_data == "menu_settings":
        await query.answer()
        settings_text = (
            "╔════════════════════════════════╗\n"
            "║  ⚙️ НАЛАШТУВАННЯ  ║\n"
            "╚════════════════════════════════╝\n\n"
            "🔧 <b>Налаштування системи:</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ Автоматичне виконання: <b>Вкл</b>\n"
            "✅ Сповіщення: <b>Вкл</b>\n"
            "✅ Логування: <b>Вкл</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📱 <i>Більше налаштувань скоро...</i>"
        )
        await query.message.answer(settings_text, parse_mode="HTML")
    
    elif callback_data == "menu_status":
        await query.answer()
        status_text = (
            "╔════════════════════════════════╗\n"
            "║  📊 СТАТУС СИСТЕМИ  ║\n"
            "╚════════════════════════════════╝\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 <b>Бот:</b> <code>АКТИВНИЙ</code>\n"
            "🟢 <b>Система:</b> <code>ГОТОВА</code>\n"
            "🟢 <b>Користувач:</b> <code>АУТЕНТИФІКОВАНИЙ</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⏱️ <b>Час роботи:</b> <code>24/7</code>\n"
            "📡 <b>Сигнал:</b> <code>Відмінний</code>"
        )
        await query.message.answer(status_text, parse_mode="HTML")
    
    elif callback_data == "menu_help":
        await query.answer()
        help_text = (
            "╔════════════════════════════════╗\n"
            "║  ❓ ДОВІДКА  ║\n"
            "╚════════════════════════════════╝\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>📱 Основні команди:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "/start - Головне меню\n"
            "/screenshot - Скріншот екрану\n"
            "/changes - Список змін\n"
            "/status - Статус системи\n"
            "/help - Ця довідка\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>💡 Поради:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "• Використовуйте кнопки для швидкого доступу\n"
            "• Пишіть завдання природною мовою\n"
            "• Перевіряйте статус перед виконанням\n\n"
            "🆘 <i>Потрібна допомога? Напишіть /support</i>"
        )
        await query.message.answer(help_text, parse_mode="HTML")
    
    elif callback_data == "menu_logout":
        await query.answer()
        auth_manager.logout(user_id)
        await query.message.answer("👋 Ви вийшли. Введіть /start для входу")
    
    # Кнопки для змін
    elif callback_data.startswith("accept_"):
        change_id = callback_data.replace("accept_", "")
        success, msg = accept_change(change_id)
        await query.answer(msg, show_alert=True)
        
        if success:
            await query.message.edit_text(
                query.message.text + "\n\n✅ <b>Прийнято!</b>",
                parse_mode="HTML"
            )
            logger.info(f"Change accepted by user {user_id}: {change_id}")
    
    elif callback_data.startswith("reject_"):
        change_id = callback_data.replace("reject_", "")
        success, msg = reject_change(change_id)
        await query.answer(msg, show_alert=True)
        
        if success:
            await query.message.edit_text(
                query.message.text + "\n\n❌ <b>Відхилено!</b>",
                parse_mode="HTML"
            )
            logger.info(f"Change rejected by user {user_id}: {change_id}")


# JULES: I've changed the decorator for this function to specifically handle
# messages from the Mini App. This ensures that these messages are
# always processed by this handler, even if the bot is in a different state.
@dp.message(F.web_app_data)
async def handle_message(message: Message):
    """Обробка звичайних повідомлень та даних з Mini App"""
    # Debug: Log ALL messages to see if handler is called
    await message.answer(f"DEBUG: Handler called! Text: {message.text}")
    logger.info(f"Handler called! Text: {message.text}, web_app_data: {message.web_app_data}")
    
    # Handle Mini App data first
    if message.web_app_data:
        try:
            data = json.loads(message.web_app_data.data)
            logger.info(f"Received Mini App data: {data}")
            await message.answer(f"DEBUG: Got data: {data}")
            
            user_id = message.from_user.id
            if not auth_manager.is_authenticated(user_id):
                await message.answer("❌ Спочатку авторизуйтесь: /start")
                return
            
            # Handle different command types
            if data.get('type') == 'command':
                # Handle single command from Mini App
                await message.answer("DEBUG: Executing command...")
                await execute_single_command(message, data)
            elif data.get('type') == 'screenshot':
                await handle_screenshot_command(message)
            elif data.get('type') == 'ai_raw':
                task_text = data.get('command', '')
                if task_text:
                    await handle_ai_task(message, task_text)
            elif data.get('type') == 'sequence':
                # Handle sequence of commands
                tasks = data.get('tasks', [])
                for task in tasks:
                    await execute_single_command(message, task)
            else:
                # Handle single command
                await execute_single_command(message, data)
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from Mini App: {message.web_app_data.data}")
            await message.answer("❌ Помилка обробки команди")
        except Exception as e:
            logger.error(f"Error handling Mini App data: {e}")
            await message.answer("❌ Помилка виконання команди")
        return

@dp.message()
async def handle_unknown_message(message: Message):
    """Handles any message that is not a command or from the Mini App."""
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ заборонений")
        return

    await message.answer(
        "❓ Не розумію команду.\n"
        "Використовуй /help для списку команд"
    )


async def execute_single_command(message: Message, command_data):
    """Execute a single command from Mini App"""
    try:
        action = command_data.get('action', '')
        
        # Handle screenshot from Mini App
        if action == 'screenshot':
            await handle_screenshot_command(message)
        elif action == 'click_center':
            await message.answer("🖱️ Клік по центру екрану")
            await executor.click.click_center()
            await message.answer("✅ Клік виконано!")
        elif action == 'open_url':
            url = command_data.get('url', '')
            await message.answer(f"🌐 Відкриття URL: {url}")
            await executor.windows.open_url(url)
            await message.answer("✅ URL відкрито!")
        elif action == 'switch_tab':
            number = command_data.get('number', 1)
            await message.answer(f"🔄 Перемикання на вкладку {number}")
            await executor.keyboard.press_hotkey(['ctrl', str(number)])
            await message.answer("✅ Вкладку перемкнуто!")
        elif action == 'run_program':
            path = command_data.get('path', '')
            await message.answer(f"🚀 Запуск програми: {path}")
            await executor.windows.run_program(path)
            await message.answer("✅ Програму запущено!")
        elif action == 'type':
            text = command_data.get('target', '')
            if text:
                await message.answer(f"✍️ Введення тексту: {text}")
                # Actually type the text
                await executor.keyboard.type_text(text)
                await message.answer("✅ Текст введено!")
        elif action == 'click':
            coords = command_data.get('target', '')
            if coords:
                await message.answer(f"🖱️ Клік: {coords}")
                # Parse coordinates if provided
                if isinstance(coords, str) and ',' in coords:
                    x, y = map(int, coords.split(','))
                    await executor.click.click_at(x, y)
                    await message.answer("✅ Клік виконано!")
                else:
                    # Click at center
                    await executor.click.click_center()
                    await message.answer("✅ Клік по центру!")
        elif action == 'open_app':
            app = command_data.get('target', '')
            if app:
                await message.answer(f"🚀 Відкриття додатку: {app}")
                # Actually open the app
                await executor.windows.open_application(app)
                await message.answer(f"✅ Додаток {app} відкрито!")
        elif action == 'hotkey':
            keys = command_data.get('keys', [])
            if keys:
                await message.answer(f"⌨️ Гаряча клавіша: {'+'.join(keys)}")
                # Actually press the hotkey
                await executor.keyboard.press_hotkey(keys)
                await message.answer("✅ Гарячу клавішу натиснуто!")
        elif action == 'wait':
            seconds = command_data.get('seconds', 1)
            await message.answer(f"⏳ Очікування: {seconds} секунд")
            await asyncio.sleep(seconds)
            await message.answer("✅ Очікування завершено!")
        elif action == 'move_mouse':
            x = command_data.get('x', 0)
            y = command_data.get('y', 0)
            await message.answer(f"🖱️ Переміщення миші до ({x}, {y})")
            await executor.click.move_to(x, y)
            await message.answer("✅ Миш переміщено!")
        else:
            await message.answer(f"⚡ Виконання: {action}")
            # Try to execute with the executor
            try:
                result = await executor.execute(command_data)
                await message.answer(f"✅ Команду виконано!")
            except:
                await message.answer(f"⚠️ Команда {action} не реалізована")
            
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        await message.answer("❌ Помилка виконання команди")


async def handle_ai_task(message: Message, task_text: str):
    """Handle AI task interpretation"""
    try:
        # Interpret task with Gemini
        task = await task_interpreter.interpret(task_text)
        
        # Execute the task
        result = await executor.execute(task)
        
        await message.answer(f"✅ Завдання виконано: {task_text}")
        
    except Exception as e:
        logger.error(f"AI task error: {e}")
        await message.answer(f"❌ Помилка виконання: {task_text}")


async def handle_screenshot_command(message: Message):
    """Handle screenshot command"""
    try:
        screen = ScreenCapture()
        path = screen.capture()
        photo = FSInputFile(path)
        await message.answer_photo(
            photo,
            caption="📸 <b>Скріншот екрану</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        await message.answer("❌ Помилка створення скріншота")


async def main():
    """Запуск бота та Mini App сервера"""
    logger.info("🚀 Starting Telegram bot...")
    logger.info(f"Admin ID: {ADMIN_ID}")
    
    # Start Mini App server
    mini_app_runner = None
    try:
        mini_app_runner = await start_mini_app_server(port=8080)
        logger.info("📱 Mini App server started on http://localhost:8080")
        logger.info("🎮 Open Telegram and click the PC Control button!")
    except Exception as e:
        logger.warning(f"Could not start Mini App server: {e}")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        if mini_app_runner:
            await stop_mini_app_server(mini_app_runner)
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
