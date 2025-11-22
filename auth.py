import logging
import os
import hashlib
from dotenv import load_dotenv
from persistence import save_users, load_users, save_user_password, verify_user_password

load_dotenv()
logger = logging.getLogger(__name__)

# Один пароль для всіх користувачів
MASTER_PASSWORD = "Ml120998"

# Завантажуємо збережених користувачів
registered_users = load_users()


def hash_password(password: str) -> str:
    """Хешує пароль"""
    return hashlib.sha256(password.encode()).hexdigest()


class AuthManager:
    """Менеджер аутентифікації"""
    
    def __init__(self):
        self.registered_users = registered_users
        self.authenticated_users = set()
    
    def register_user(self, user_id: int, username: str, password: str) -> tuple[bool, str]:
        """
        Реєструє нового користувача
        
        Args:
            user_id: Telegram ID
            username: Ім'я користувача
            password: Пароль
            
        Returns:
            (успіх, повідомлення)
        """
        try:
            # Перевіряємо пароль
            if password != MASTER_PASSWORD:
                logger.warning(f"Failed registration attempt for user {user_id}: wrong password")
                return False, "❌ Неправильний пароль!"
            
            # Перевіряємо, чи користувач вже зареєстрований
            if user_id in self.registered_users:
                return False, "⚠️ Ви вже зареєстровані!"
            
            # Реєструємо користувача
            password_hash = hash_password(password)
            
            self.registered_users[str(user_id)] = {
                'username': username,
                'user_id': user_id,
                'authenticated': True,
                'password_hash': password_hash
            }
            
            self.authenticated_users.add(user_id)
            
            # Зберігаємо в файл з хешованим паролем
            save_user_password(user_id, username, password_hash)
            
            logger.info(f"User {user_id} ({username}) registered successfully with password hash")
            return True, f"✅ Ви зареєстровані як '{username}'!"
        
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"❌ Помилка реєстрації: {str(e)}"
    
    def authenticate_user(self, user_id: int, password: str) -> tuple[bool, str]:
        """
        Аутентифікує користувача
        
        Args:
            user_id: Telegram ID
            password: Пароль
            
        Returns:
            (успіх, повідомлення)
        """
        try:
            # Перевіряємо, чи користувач зареєстрований
            if str(user_id) not in self.registered_users:
                logger.warning(f"Authentication attempt for unregistered user {user_id}")
                return False, "❌ Користувач не зареєстрований! Використовуйте /register"
            
            # Перевіряємо пароль (хешований)
            user = self.registered_users[str(user_id)]
            stored_hash = user.get('password_hash', '')
            password_hash = hash_password(password)
            
            if password_hash != stored_hash:
                logger.warning(f"Failed authentication attempt for user {user_id}: wrong password")
                return False, "❌ Неправильний пароль!"
            
            # Аутентифікуємо користувача
            self.authenticated_users.add(user_id)
            
            username = user['username']
            logger.info(f"User {user_id} ({username}) authenticated successfully")
            return True, f"✅ Ви аутентифіковані як '{username}'!"
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, f"❌ Помилка аутентифікації: {str(e)}"
    
    def is_authenticated(self, user_id: int) -> bool:
        """Перевіряє, чи користувач аутентифікований"""
        return user_id in self.authenticated_users
    
    def is_registered(self, user_id: int) -> bool:
        """Перевіряє, чи користувач зареєстрований"""
        return user_id in self.registered_users
    
    def get_username(self, user_id: int) -> str:
        """Отримує ім'я користувача"""
        if user_id in self.registered_users:
            return self.registered_users[user_id]['username']
        return "Unknown"
    
    def logout_user(self, user_id: int) -> tuple[bool, str]:
        """Виходить з системи"""
        try:
            if user_id in self.authenticated_users:
                self.authenticated_users.remove(user_id)
                logger.info(f"User {user_id} logged out")
                return True, "✅ Ви вийшли з системи!"
            return False, "⚠️ Ви не аутентифіковані"
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False, f"❌ Помилка виходу: {str(e)}"
    
    def get_stats(self) -> dict:
        """Отримує статистику"""
        return {
            'registered': len(self.registered_users),
            'authenticated': len(self.authenticated_users),
            'users': list(self.registered_users.keys())
        }
