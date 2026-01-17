#!/usr/bin/env python3
"""
HTTP MJPEG Stream Server for USB Cameras on Jetson
Streams both cameras simultaneously on different endpoints
"""

import subprocess
import socketserver
import threading
from http.server import BaseHTTPRequestHandler
import signal
import sys

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream1.mjpg':
            self.stream_camera('/dev/video0')
        elif self.path == '/stream2.mjpg':
            self.stream_camera('/dev/video2')
        elif self.path == '/':
            self.send_html_page()
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_html_page(self):
        """Send HTML page with both streams embedded"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Live Camera Streams</title>
    <style>
        body { margin: 0; background: #000; }
        .container { display: flex; width: 100vw; height: 100vh; }
        .camera { flex: 1; display: flex; flex-direction: column; }
        .camera h2 { color: white; text-align: center; margin: 10px; }
        .camera img { width: 100%; height: 100%; object-fit: contain; }
    </style>
</head>
<body>
    <div class="container">
        <div class="camera">
            <h2>Camera 1</h2>
            <img src="/stream1.mjpg" alt="Camera 1">
        </div>
        <div class="camera">
            <h2>Camera 2</h2>
            <img src="/stream2.mjpg" alt="Camera 2">
        </div>
    </div>
</body>
</html>"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def stream_camera(self, device):
        """Stream MJPEG from camera device"""
        self.send_response(200)
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--boundary')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Pragma', 'no-cache')
        self.end_headers()
        
        # Start ffmpeg process
        ffmpeg = subprocess.Popen(
            ['ffmpeg',
             '-f', 'v4l2',
             '-input_format', 'mjpeg',
             '-video_size', '1280x720',
             '-framerate', '30',
             '-i', device,
             '-f', 'mjpeg',
             '-q:v', '3',
             '-an',
             '-'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10**8
        )
        
        try:
            while True:
                chunk = ffmpeg.stdout.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            ffmpeg.terminate()
            ffmpeg.wait()
    
    def log_message(self, format, *args):
        # Suppress logging
        pass

def run_server(port=8080):
    """Run the streaming server"""
    class TCPServer(socketserver.TCPServer):
        allow_reuse_address = True
    
    with TCPServer(("", port), StreamingHandler) as httpd:
        print(f"Camera streaming server started")
        print(f"View both cameras: http://0.0.0.0:{port}/")
        print(f"Camera 1 only: http://0.0.0.0:{port}/stream1.mjpg")
        print(f"Camera 2 only: http://0.0.0.0:{port}/stream2.mjpg")
        print("Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            httpd.shutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)

