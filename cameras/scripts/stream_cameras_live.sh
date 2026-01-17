#!/bin/bash
# Live video streaming from both USB cameras via HTTP MJPEG streams

set -e

PORT1=8080
PORT2=8081

echo "=========================================="
echo "Starting Live Camera Streams"
echo "=========================================="
echo "Camera 1: http://$(hostname -I | awk '{print $1}'):$PORT1/stream.mjpg"
echo "Camera 2: http://$(hostname -I | awk '{print $1}'):$PORT1/stream2.mjpg"
echo "=========================================="
echo "Press Ctrl+C to stop"
echo ""

# Function to stream camera
stream_camera() {
    local device=$1
    local port=$2
    local stream_name=$3
    
    ffmpeg -f v4l2 \
           -input_format mjpeg \
           -video_size 1280x720 \
           -framerate 30 \
           -i "$device" \
           -vf "format=yuv420p" \
           -f mjpeg \
           -q:v 5 \
           -an \
           - 2>/dev/null | \
    while IFS= read -r line; do
        echo -ne "HTTP/1.0 200 OK\r\n"
        echo -ne "Content-Type: multipart/x-mixed-replace; boundary=boundary\r\n\r\n"
        break
    done
}

# Start Camera 1 stream on port 8080
start_camera1() {
    echo "Starting Camera 1 stream on port $PORT1..."
    while true; do
        ffmpeg -f v4l2 \
               -input_format mjpeg \
               -video_size 1280x720 \
               -framerate 30 \
               -i /dev/video0 \
               -f mjpeg \
               -q:v 3 \
               -an \
               - 2>/dev/null | \
        (echo -ne "HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=--boundary\r\n\r\n"; cat -) | \
        nc -l -p $PORT1 2>/dev/null || \
        (echo -ne "HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=--boundary\r\n\r\n"; \
         ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -framerate 30 -i /dev/video0 -f mjpeg -q:v 3 -an - 2>/dev/null)
    done
}

# Start Camera 2 stream on port 8081
start_camera2() {
    echo "Starting Camera 2 stream on port $PORT2..."
    while true; do
        ffmpeg -f v4l2 \
               -input_format mjpeg \
               -video_size 1280x720 \
               -framerate 30 \
               -i /dev/video2 \
               -f mjpeg \
               -q:v 3 \
               -an \
               - 2>/dev/null | \
        (echo -ne "HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=--boundary\r\n\r\n"; cat -) | \
        nc -l -p $PORT2 2>/dev/null || \
        (echo -ne "HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=--boundary\r\n\r\n"; \
         ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -framerate 30 -i /dev/video2 -f mjpeg -q:v 3 -an - 2>/dev/null)
    done
}

# Check if netcat is available, if not use Python HTTP server
if command -v python3 &> /dev/null; then
    echo "Using Python HTTP server for MJPEG streams..."
    
    # Create Python script for streaming
    cat > /tmp/camera_streamer.py << 'PYEOF'
#!/usr/bin/env python3
import subprocess
import socketserver
import threading
from http.server import BaseHTTPRequestHandler
import sys

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream1.mjpg':
            self.stream_camera('/dev/video0')
        elif self.path == '/stream2.mjpg':
            self.stream_camera('/dev/video2')
        else:
            self.send_response(404)
            self.end_headers()
    
    def stream_camera(self, device):
        self.send_response(200)
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--boundary')
        self.end_headers()
        
        ffmpeg = subprocess.Popen(
            ['ffmpeg', '-f', 'v4l2',
             '-input_format', 'mjpeg',
             '-video_size', '1280x720',
             '-framerate', '30',
             '-i', device,
             '-f', 'mjpeg',
             '-q:v', '3',
             '-an',
             '-'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        
        try:
            while True:
                frame = ffmpeg.stdout.read(1024)
                if not frame:
                    break
                self.wfile.write(frame)
        except:
            pass
        finally:
            ffmpeg.terminate()
            ffmpeg.wait()
    
    def log_message(self, format, *args):
        pass

def run_server():
    port = 8080
    with socketserver.TCPServer(("", port), StreamingHandler) as httpd:
        print(f"Server running on port {port}")
        print(f"Camera 1: http://0.0.0.0:{port}/stream1.mjpg")
        print(f"Camera 2: http://0.0.0.0:{port}/stream2.mjpg")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()
PYEOF
    
    chmod +x /tmp/camera_streamer.py
    python3 /tmp/camera_streamer.py
    
else
    # Fallback: Start separate processes
    start_camera1 &
    CAM1_PID=$!
    start_camera2 &
    CAM2_PID=$!
    
    echo "Streams started. PIDs: Camera1=$CAM1_PID, Camera2=$CAM2_PID"
    echo "Press Ctrl+C to stop..."
    
    wait
fi
