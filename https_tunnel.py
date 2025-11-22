import ssl
import logging
from aiohttp import web
import os
from pathlib import Path

logger = logging.getLogger(__name__)

MINI_APP_DIR = os.path.join(os.path.dirname(__file__), 'mini-app', 'dist')


async def serve_mini_app(request):
    """Serve Mini App static files"""
    path = request.match_info.get('path', 'index.html')
    
    if '..' in path:
        return web.Response(status=403, text='Forbidden')
    
    file_path = os.path.join(MINI_APP_DIR, path)
    
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        file_path = os.path.join(MINI_APP_DIR, 'index.html')
    
    if not os.path.exists(file_path):
        return web.Response(status=404, text='Not Found')
    
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


def create_self_signed_cert():
    """Create self-signed certificate for HTTPS"""
    import subprocess
    
    cert_dir = os.path.join(os.path.dirname(__file__), 'certs')
    os.makedirs(cert_dir, exist_ok=True)
    
    cert_file = os.path.join(cert_dir, 'cert.pem')
    key_file = os.path.join(cert_dir, 'key.pem')
    
    # Check if cert already exists
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return cert_file, key_file
    
    # Create self-signed certificate
    try:
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', key_file, '-out', cert_file,
            '-days', '365', '-nodes',
            '-subj', '/CN=localhost'
        ], check=True, capture_output=True)
        logger.info(f"✅ Created self-signed certificate")
        return cert_file, key_file
    except Exception as e:
        logger.warning(f"Could not create certificate: {e}")
        return None, None


async def start_https_server(port=8443):
    """Start HTTPS server for Mini App"""
    app = web.Application()
    
    app.router.add_get('/health', health_check)
    app.router.add_get('/{path:.*}', serve_mini_app)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Try to use HTTPS
    ssl_context = None
    try:
        cert_file, key_file = create_self_signed_cert()
        if cert_file and key_file:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(cert_file, key_file)
            logger.info(f"✅ HTTPS Mini App server started on https://localhost:{port}")
            logger.info(f"📱 Mini App URL: https://localhost:{port}")
        else:
            logger.warning("Using HTTP instead of HTTPS")
    except Exception as e:
        logger.warning(f"HTTPS setup failed: {e}, using HTTP")
    
    site = web.TCPSite(runner, '0.0.0.0', port, ssl_context=ssl_context)
    await site.start()
    
    return runner


async def stop_https_server(runner):
    """Stop HTTPS server"""
    await runner.cleanup()
    logger.info("HTTPS server stopped")
