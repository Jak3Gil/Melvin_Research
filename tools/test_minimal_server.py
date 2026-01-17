#!/usr/bin/env python3
"""Minimal test server to verify connectivity"""

from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Test Server Working!</h1>')
    
    def log_message(self, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), Handler)
    print("Test server starting on 0.0.0.0:8080...")
    server.serve_forever()

