#!/usr/bin/env python3
"""
Live MJPEG streaming server for USB cameras
Streams both cameras simultaneously via HTTP
"""

import subprocess
import threading
import socketserver
from http import server
import sys
import signal

PORT1 = 8080
PORT2 = 8081

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            try:
                while True:
                    # Read frame from stdin (piped from ffmpeg)
                    frame_data = sys.stdin.buffer.read(10240)  # Read in chunks
                    if not frame_data:
                        break
                    self.wfile.write(b'--jpgboundary\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(frame_data)))
                    self.end_headers()
                    self.wfile.write(frame_data)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                print(f"Stream error: {e}")
        else:
            self.send_error(404)

def stream_camera(device, port, camera_name):
    """Stream camera using ffmpeg and Python HTTP server"""
    print(f"Starting {camera_name} stream on port {port}...")
    
    # FFmpeg command to capture and output MJPEG
    ffmpeg_cmd = [
        'ffmpeg',
        '-f', 'v4l2',
        '-input_format', 'mjpeg',
        '-video_size', '1280x720',
        '-framerate', '30',
        '-i', device,
        '-f', 'mjpeg',
        '-q:v', '3',
        '-'  # Output to stdout
    ]
    
    try:
        # Start ffmpeg
        ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        
        # Create HTTP server that reads from ffmpeg stdout
        class FrameStreamHandler(server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/stream.mjpg':
                    self.send_response(200)
                    self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
                    self.end_headers()
                    try:
                        while True:
                            frame = ffmpeg_process.stdout.read(8192)
                            if not frame:
                                break
                            self.wfile.write(b'--jpgboundary\r\n')
                            self.send_header('Content-Type', 'image/jpeg')
                            self.send_header('Content-Length', str(len(frame)))
                            self.end_headers()
                            self.wfile.write(frame)
                            self.wfile.write(b'\r\n')
                    except:
                        pass
                else:
                    self.send_error(404)
            
            def log_message(self, format, *args):
                pass  # Suppress log messages
        
        httpd = socketserver.TCPServer(('0.0.0.0', port), FrameStreamHandler)
        print(f"{camera_name} stream ready at http://0.0.0.0:{port}/stream.mjpg")
        httpd.serve_forever()
        
    except Exception as e:
        print(f"Error streaming {camera_name}: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) > 1:
        port1 = int(sys.argv[1])
        port2 = int(sys.argv[2])
    else:
        port1 = PORT1
        port2 = PORT2
    
    print("=" * 50)
    print("Live Camera Streaming Server")
    print("=" * 50)
    print(f"Camera 1: http://$(hostname -I):{port1}/stream.mjpg")
    print(f"Camera 2: http://$(hostname -I):{port2}/stream.mjpg")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    print()
    
    # Start both streams in separate threads
    thread1 = threading.Thread(
        target=stream_camera,
        args=('/dev/video0', port1, 'Camera 1'),
        daemon=True
    )
    thread2 = threading.Thread(
        target=stream_camera,
        args=('/dev/video2', port2, 'Camera 2'),
        daemon=True
    )
    
    thread1.start()
    thread2.start()
    
    try:
        # Keep main thread alive
        thread1.join()
        thread2.join()
    except KeyboardInterrupt:
        print("\nStopping streams...")
        sys.exit(0)

if __name__ == '__main__':
    main()

