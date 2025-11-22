import asyncio
import logging
from aiohttp import web
import os

logger = logging.getLogger(__name__)

MINI_APP_DIR = os.path.join(os.path.dirname(__file__), 'mini-app', 'dist')


async def serve_mini_app(request):
    """Serve Mini App static files"""
    path = request.match_info.get('path', 'index.html')
    
    # Security: prevent directory traversal
    if '..' in path:
        return web.Response(status=403, text='Forbidden')
    
    file_path = os.path.join(MINI_APP_DIR, path)
    
    # If it's a directory or doesn't exist, serve index.html
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        file_path = os.path.join(MINI_APP_DIR, 'index.html')
    
    if not os.path.exists(file_path):
        return web.Response(status=404, text='Not Found')
    
    # Determine content type
    content_type = 'text/html'
    if file_path.endswith('.js'):
        content_type = 'application/javascript'
    elif file_path.endswith('.css'):
        content_type = 'text/css'
    elif file_path.endswith('.json'):
        content_type = 'application/json'
    elif file_path.endswith('.png'):
        content_type = 'image/png'
    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        content_type = 'image/jpeg'
    elif file_path.endswith('.svg'):
        content_type = 'image/svg+xml'
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return web.Response(body=content, content_type=content_type)
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {e}")
        return web.Response(status=500, text='Internal Server Error')


async def health_check(request):
    """Health check endpoint"""
    return web.json_response({'status': 'ok'})


async def start_mini_app_server(port=8080):
    """Start the Mini App server"""
    app = web.Application()
    
    # Routes
    app.router.add_get('/health', health_check)
    app.router.add_get('/{path:.*}', serve_mini_app)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"✅ Mini App server started on http://localhost:{port}")
    logger.info(f"📱 Mini App URL: http://localhost:{port}")
    
    return runner


async def stop_mini_app_server(runner):
    """Stop the Mini App server"""
    await runner.cleanup()
    logger.info("Mini App server stopped")
