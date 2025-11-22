import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

USERS_FILE = "data/users.json"
TASKS_FILE = "data/tasks.json"


def ensure_data_dir():
    """Створює папку data якщо не існує"""
    os.makedirs("data", exist_ok=True)


def save_users(users_dict: dict):
    """Зберігає користувачів в JSON"""
    try:
        ensure_data_dir()
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_dict, f, indent=2, ensure_ascii=False)
        logger.info(f"Users saved: {len(users_dict)} users")
    except Exception as e:
        logger.error(f"Error saving users: {e}")


def load_users() -> dict:
    """Завантажує користувачів з JSON"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
            logger.info(f"Users loaded: {len(users)} users")
            return users
        return {}
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return {}


def save_user_password(user_id: int, username: str, password_hash: str):
    """Зберігає пароль користувача (хешований)"""
    try:
        ensure_data_dir()
        
        # Завантажуємо існуючих користувачів
        users = load_users()
        
        # Додаємо/оновлюємо користувача з паролем
        users[str(user_id)] = {
            'username': username,
            'user_id': user_id,
            'password_hash': password_hash,
            'registered_at': datetime.now().isoformat()
        }
        
        # Зберігаємо
        save_users(users)
        logger.info(f"User password saved for {user_id}")
    except Exception as e:
        logger.error(f"Error saving user password: {e}")


def verify_user_password(user_id: int, password: str) -> bool:
    """Перевіряє пароль користувача"""
    try:
        users = load_users()
        
        if str(user_id) not in users:
            return False
        
        user = users[str(user_id)]
        stored_hash = user.get('password_hash', '')
        
        # Простий хеш для демонстрації (в реальній системі використовувати bcrypt)
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        return password_hash == stored_hash
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def save_task(user_id: int, task_text: str, status: str = "pending"):
    """Зберігає завдання в JSON"""
    try:
        ensure_data_dir()
        
        # Завантажуємо існуючі завдання
        tasks = {}
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
        
        # Додаємо нове завдання
        task_id = len(tasks) + 1
        tasks[str(task_id)] = {
            'user_id': user_id,
            'task': task_text,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        # Зберігаємо
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Task saved: {task_id} for user {user_id}")
        return task_id
    except Exception as e:
        logger.error(f"Error saving task: {e}")
        return None


def get_all_tasks() -> dict:
    """Отримує всі завдання"""
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading tasks: {e}")
        return {}


def write_to_windsurf(task_text: str, user_id: int = 0):
    """Пише завдання в файл для Windsurf"""
    try:
        ensure_data_dir()
        
        windsurf_file = "data/windsurf_tasks.txt"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(windsurf_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{timestamp}] User {user_id}\n")
            f.write(f"Task: {task_text}\n")
            f.write(f"{'='*60}\n")
        
        logger.info(f"Task written to Windsurf: {task_text[:50]}...")
        return True
    except Exception as e:
        logger.error(f"Error writing to Windsurf: {e}")
        return False
