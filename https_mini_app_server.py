#!/usr/bin/env python3
import ssl
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for Telegram
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Serve index.html for all routes (SPA routing)
        if self.path == '/' or not self.path.startswith('/assets/'):
            self.path = '/index.html'
        return super().do_GET()

def start_https_server(port=8443):
    """Start HTTPS server for Mini App"""
    
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mini_app_dir = os.path.join(script_dir, 'mini-app', 'dist')
    cert_dir = os.path.join(script_dir, 'certs')
    cert_file = os.path.join(cert_dir, 'cert.pem')
    key_file = os.path.join(cert_dir, 'key.pem')
    
    # Check if mini-app dist exists
    if not os.path.exists(mini_app_dir):
        print(f"❌ Mini App dist folder not found at {mini_app_dir}")
        print("Run: npm run build in mini-app folder first")
        sys.exit(1)
    
    # Create certificate if needed
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("Creating HTTPS certificate...")
        os.system(f"{sys.executable} setup_https.py")
    
    # Check if certificate exists now
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print(f"❌ Certificate not found at {cert_file}")
        sys.exit(1)
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    
    # Create server
    handler = lambda *args, **kwargs: MyHTTPRequestHandler(
        *args, 
        directory=mini_app_dir,
        **kwargs
    )
    
    server = HTTPServer(('0.0.0.0', port), handler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    
    print(f"\n{'='*50}")
    print(f"✅ HTTPS Mini App Server Started!")
    print(f"{'='*50}")
    print(f"🔒 URL: https://localhost:{port}")
    print(f"📁 Serving: {mini_app_dir}")
    print(f"🔐 Certificate: {cert_file}")
    print(f"\n⚠️  Note: Browser will warn about self-signed cert")
    print(f"   This is normal for local testing")
    print(f"\n📱 Use this URL in BotFather:")
    print(f"   https://localhost:{port}")
    print(f"\n💡 Or for network access:")
    print(f"   https://192.168.178.34:{port}")
    print(f"{'='*50}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
        sys.exit(0)

if __name__ == '__main__':
    port = 8443
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    start_https_server(port)
