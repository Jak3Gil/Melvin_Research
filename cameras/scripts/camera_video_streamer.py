#!/usr/bin/env python3
"""
Video Stream Server for USB Cameras
Streams H.264 video via HTTP or UDP for real-time viewing
"""

import subprocess
import socketserver
from http.server import BaseHTTPRequestHandler
import threading
import sys

class VideoStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/camera1':
            self.stream_video('/dev/video0')
        elif self.path == '/camera2':
            self.stream_video('/dev/video2')
        else:
            self.send_response(404)
            self.end_headers()
    
    def stream_video(self, device):
        """Stream H.264 video via HTTP"""
        self.send_response(200)
        self.send_header('Content-Type', 'video/mp4')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Pragma', 'no-cache')
        self.end_headers()
        
        # Use ffmpeg to stream H.264 video
        ffmpeg = subprocess.Popen(
            ['ffmpeg',
             '-f', 'v4l2',
             '-input_format', 'mjpeg',
             '-video_size', '1280x720',
             '-framerate', '30',
             '-i', device,
             '-c:v', 'libx264',
             '-preset', 'ultrafast',
             '-tune', 'zerolatency',
             '-g', '30',
             '-f', 'mp4',
             '-movflags', 'frag_keyframe+empty_moov',
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
        pass

def run_server(port=8080):
    """Run the video streaming server"""
    class TCPServer(socketserver.TCPServer):
        allow_reuse_address = True
    
    with TCPServer(("", port), VideoStreamHandler) as httpd:
        print(f"Video streaming server started on port {port}")
        print(f"Camera 1: http://0.0.0.0:{port}/camera1")
        print(f"Camera 2: http://0.0.0.0:{port}/camera2")
        print("Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            httpd.shutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)

