#!/usr/bin/env python3
"""
Simple HTTP MJPEG Video Server
Streams live video from cameras via HTTP for maximum compatibility
"""

import subprocess
import socketserver
from http.server import BaseHTTPRequestHandler
import threading
import sys
import time

class MJPEGHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream1.mjpg':
            self.stream_camera('/dev/video0')
        elif self.path == '/stream2.mjpg':
            self.stream_camera('/dev/video2')
        elif self.path == '/':
            self.send_index()
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_index(self):
        """Send HTML page with embedded streams"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Live Camera Streams</title>
    <style>
        body { margin: 0; background: #000; font-family: Arial; }
        .container { display: flex; width: 100vw; height: 100vh; }
        .camera { flex: 1; display: flex; flex-direction: column; border: 2px solid #333; }
        .camera h2 { color: white; text-align: center; margin: 10px; }
        .camera img { width: 100%; height: calc(100% - 50px); object-fit: contain; }
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
        """Stream MJPEG from camera"""
        self.send_response(200)
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Connection', 'close')
        self.end_headers()
        
        try:
            # Use ffmpeg to stream MJPEG frames
            # Add probe size and analyzeduration for camera 2 compatibility
            ffmpeg = subprocess.Popen(
                ['ffmpeg',
                 '-fflags', 'nobuffer',
                 '-flags', 'low_delay',
                 '-strict', 'experimental',
                 '-f', 'v4l2',
                 '-input_format', 'mjpeg',
                 '-video_size', '1280x720',
                 '-framerate', '30',
                 '-probesize', '32',
                 '-analyzeduration', '0',
                 '-i', device,
                 '-f', 'mjpeg',
                 '-q:v', '3',
                 '-'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
            
            while True:
                # Read JPEG frame
                frame_data = b''
                jpeg_start = False
                
                while True:
                    chunk = ffmpeg.stdout.read(4096)
                    if not chunk:
                        return
                    
                    frame_data += chunk
                    
                    # Look for JPEG start
                    if b'\xff\xd8' in frame_data:
                        jpeg_start = True
                        idx = frame_data.index(b'\xff\xd8')
                        frame_data = frame_data[idx:]
                    
                    # Look for JPEG end
                    if jpeg_start and b'\xff\xd9' in frame_data:
                        idx = frame_data.index(b'\xff\xd9')
                        jpeg = frame_data[:idx+2]
                        frame_data = frame_data[idx+2:]
                        
                        # Send frame
                        try:
                            self.wfile.write(b'--jpgboundary\r\n')
                            self.wfile.write(b'Content-Type: image/jpeg\r\n')
                            self.wfile.write(f'Content-Length: {len(jpeg)}\r\n'.encode())
                            self.wfile.write(b'\r\n')
                            self.wfile.write(jpeg)
                            self.wfile.write(b'\r\n')
                            break
                        except (ConnectionResetError, BrokenPipeError):
                            return
        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                ffmpeg.terminate()
                ffmpeg.wait()
            except:
                pass
    
    def log_message(self, format, *args):
        pass

def run_server(port=8080):
    from http.server import HTTPServer
    
    server = HTTPServer(("0.0.0.0", port), MJPEGHandler)
    print(f"HTTP MJPEG server started on port {port}", flush=True)
    print(f"View in browser: http://0.0.0.0:{port}/", flush=True)
    print(f"Camera 1: http://0.0.0.0:{port}/stream1.mjpg", flush=True)
    print(f"Camera 2: http://0.0.0.0:{port}/stream2.mjpg", flush=True)
    print("Server ready, waiting for connections...", flush=True)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...", flush=True)
        server.shutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)

