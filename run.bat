@echo off
REM Telegram PC Control Bot - Запуск

echo.
echo ========================================
echo 🤖 Telegram PC Control Bot
echo ========================================
echo.

REM Перевіряємо Python
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не встановлений!
    echo Завантажте з https://www.python.org/
    pause
    exit /b 1
)

REM Перевіряємо .env
if not exist ".env" (
    echo ❌ Файл .env не знайдений!
    echo Скопіюйте .env.example в .env і заповніть дані
    pause
    exit /b 1
)

REM Перевіряємо залежності
echo 🔍 Перевіряю залежності...
py -m pip install -q -r requirements.txt

REM Запускаємо бота
echo.
echo 🚀 Запускаю бота...
echo.
py main.py

pause
