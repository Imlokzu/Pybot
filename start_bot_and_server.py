#!/usr/bin/env python3
"""
Script to start both the Telegram bot and the HTTPS mini app server
"""
import asyncio
import logging
from main import bot, dp, TOKEN
from https_mini_app_server import start_https_server
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def start_bot():
    """Start the Telegram bot"""
    try:
        logger.info("Starting Telegram bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

async def run_server():
    """Run the HTTPS mini app server"""
    from aiohttp import web
    from https_tunnel import serve_mini_app, health_check
    
    app = web.Application()
    
    app.router.add_get('/health', health_check)
    app.router.add_get('/{path:.*}', serve_mini_app)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8443)
    await site.start()
    
    logger.info("🌐 HTTPS mini app server started on https://localhost:8443/")
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour, then repeat

async def main():
    """Main function to start both servers"""
    if not TOKEN or TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("❌ TELEGRAM_TOKEN не встановлений в .env")
        return

    logger.info("🚀 Starting both Telegram bot and HTTPS mini app server...")

    # Run both servers concurrently
    await asyncio.gather(
        start_bot(),
        run_server()
    )

if __name__ == "__main__":
    asyncio.run(main())