# Telegram PC Control Bot - Запуск

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🤖 Telegram PC Control Bot" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Перевіряємо Python
try {
    py --version | Out-Null
} catch {
    Write-Host "❌ Python не встановлений!" -ForegroundColor Red
    Write-Host "Завантажте з https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Натисніть Enter для виходу"
    exit 1
}

# Перевіряємо .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ Файл .env не знайдений!" -ForegroundColor Red
    Write-Host "Скопіюйте .env.example в .env і заповніть дані" -ForegroundColor Yellow
    Read-Host "Натисніть Enter для виходу"
    exit 1
}

# Перевіряємо залежності
Write-Host "🔍 Перевіряю залежності..." -ForegroundColor Yellow
py -m pip install -q -r requirements.txt

# Запускаємо бота
Write-Host ""
Write-Host "🚀 Запускаю бота..." -ForegroundColor Green
Write-Host ""

py main.py

Read-Host "Натисніть Enter для виходу"
