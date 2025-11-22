import logging
import subprocess
import os

logger = logging.getLogger(__name__)


class WindowController:
    """Клас для контролю вікон Windows"""
    
    def open_app(self, app_path: str) -> bool:
        """Відкрити додаток"""
        try:
            logger.info(f"Opening app: {app_path}")
            subprocess.Popen(app_path)
            return True
            
        except Exception as e:
            logger.error(f"Open app error: {e}")
            return False
    
    def close_app(self, window_title: str) -> bool:
        """Закрити додаток за назвою вікна"""
        try:
            logger.info(f"Closing app: {window_title}")
            os.system(f'taskkill /IM {window_title} /F')
            return True
                
        except Exception as e:
            logger.error(f"Close app error: {e}")
            return False
    
    def get_active_window(self) -> str:
        """Отримати назву активного вікна"""
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            logger.info(f"Active window: {window_title}")
            return window_title
            
        except Exception as e:
            logger.error(f"Get active window error: {e}")
            return ""
    
    def list_windows(self) -> list:
        """Отримати список всіх вікон"""
        try:
            import win32gui
            windows = []
            
            def enum_windows(hwnd, lParam):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        windows.append(title)
                return True
            
            win32gui.EnumWindows(enum_windows, None)
            logger.info(f"Found {len(windows)} windows")
            return windows
            
        except Exception as e:
            logger.error(f"List windows error: {e}")
            return []
