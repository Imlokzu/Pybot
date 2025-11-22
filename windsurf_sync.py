import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

CHANGES_FILE = "data/windsurf_changes.json"


def ensure_data_dir():
    """Створює папку data якщо не існує"""
    os.makedirs("data", exist_ok=True)


def save_windsurf_change(change_id: str, change_data: dict, status: str = "pending"):
    """Зберігає зміну Windsurf в JSON"""
    try:
        ensure_data_dir()
        
        # Завантажуємо існуючі зміни
        changes = {}
        if os.path.exists(CHANGES_FILE):
            with open(CHANGES_FILE, 'r', encoding='utf-8') as f:
                changes = json.load(f)
        
        # Додаємо/оновлюємо зміну
        changes[change_id] = {
            'id': change_id,
            'data': change_data,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        # Зберігаємо
        with open(CHANGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(changes, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Windsurf change saved: {change_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving windsurf change: {e}")
        return False


def get_pending_changes() -> list:
    """Отримує всі очікуючі зміни"""
    try:
        if not os.path.exists(CHANGES_FILE):
            return []
        
        with open(CHANGES_FILE, 'r', encoding='utf-8') as f:
            changes = json.load(f)
        
        pending = [
            change for change in changes.values() 
            if change.get('status') == 'pending'
        ]
        
        logger.info(f"Found {len(pending)} pending changes")
        return pending
    except Exception as e:
        logger.error(f"Error getting pending changes: {e}")
        return []


def accept_change(change_id: str) -> tuple:
    """Приймає зміну"""
    try:
        ensure_data_dir()
        
        if not os.path.exists(CHANGES_FILE):
            logger.warning(f"Changes file not found")
            return False, "❌ Файл змін не знайдено"
        
        with open(CHANGES_FILE, 'r', encoding='utf-8') as f:
            changes = json.load(f)
        
        if change_id not in changes:
            logger.warning(f"Change {change_id} not found")
            return False, f"❌ Зміна {change_id} не знайдена"
        
        changes[change_id]['status'] = 'accepted'
        changes[change_id]['accepted_at'] = datetime.now().isoformat()
        
        with open(CHANGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(changes, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Change accepted: {change_id}")
        return True, f"✅ Зміна {change_id} прийнята"
    except Exception as e:
        logger.error(f"Error accepting change: {e}")
        return False, f"❌ Помилка: {str(e)}"


def reject_change(change_id: str) -> tuple:
    """Відхиляє зміну"""
    try:
        ensure_data_dir()
        
        if not os.path.exists(CHANGES_FILE):
            logger.warning(f"Changes file not found")
            return False, "❌ Файл змін не знайдено"
        
        with open(CHANGES_FILE, 'r', encoding='utf-8') as f:
            changes = json.load(f)
        
        if change_id not in changes:
            logger.warning(f"Change {change_id} not found")
            return False, f"❌ Зміна {change_id} не знайдена"
        
        changes[change_id]['status'] = 'rejected'
        changes[change_id]['rejected_at'] = datetime.now().isoformat()
        
        with open(CHANGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(changes, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Change rejected: {change_id}")
        return True, f"✅ Зміна {change_id} відхилена"
    except Exception as e:
        logger.error(f"Error rejecting change: {e}")
        return False, f"❌ Помилка: {str(e)}"


def get_changes_list() -> list:
    """Отримує список всіх змін"""
    try:
        if not os.path.exists(CHANGES_FILE):
            return []
        
        with open(CHANGES_FILE, 'r', encoding='utf-8') as f:
            changes = json.load(f)
        
        changes_list = list(changes.values())
        logger.info(f"Found {len(changes_list)} changes")
        return changes_list
    except Exception as e:
        logger.error(f"Error getting changes list: {e}")
        return []


def get_accepted_changes() -> list:
    """Отримує всі прийняті зміни"""
    try:
        if not os.path.exists(CHANGES_FILE):
            return []
        
        with open(CHANGES_FILE, 'r', encoding='utf-8') as f:
            changes = json.load(f)
        
        accepted = [
            change for change in changes.values() 
            if change.get('status') == 'accepted'
        ]
        
        logger.info(f"Found {len(accepted)} accepted changes")
        return accepted
    except Exception as e:
        logger.error(f"Error getting accepted changes: {e}")
        return []


def get_next_change_id() -> str:
    """Отримує наступний ID для змін"""
    try:
        if not os.path.exists(CHANGES_FILE):
            return "change_001"
        
        with open(CHANGES_FILE, 'r', encoding='utf-8') as f:
            changes = json.load(f)
        
        if not changes:
            return "change_001"
        
        # Знаходимо максимальний номер
        max_num = 0
        for change_id in changes.keys():
            try:
                num = int(change_id.replace('change_', ''))
                max_num = max(max_num, num)
            except:
                pass
        
        return f"change_{max_num + 1:03d}"
    except Exception as e:
        logger.error(f"Error getting next change id: {e}")
        return f"change_{datetime.now().strftime('%Y%m%d%H%M%S')}"
