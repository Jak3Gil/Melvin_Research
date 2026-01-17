#!/bin/bash
# Simple MJPEG streaming using ffmpeg with proper HTTP server
# This should work better with VLC and browsers

set -e

PORT1=8091
PORT2=8092

echo "Starting MJPEG HTTP streams..."
echo "Camera 1 on port $PORT1"
echo "Camera 2 on port $PORT2"
echo ""

# Use ffmpeg's HTTP server with proper MJPEG streaming
# Camera 1 - using -re for real-time and proper HTTP
ffmpeg -f v4l2 \
       -input_format mjpeg \
       -video_size 1280x720 \
       -framerate 30 \
       -re \
       -i /dev/video0 \
       -f mjpeg \
       -q:v 3 \
       -an \
       -vf "format=yuvj420p" \
       -fflags +genpts \
       -flags low_delay \
       -strict experimental \
       -listen 1 \
       http://0.0.0.0:$PORT1 &
CAM1_PID=$!

# Camera 2
ffmpeg -f v4l2 \
       -input_format mjpeg \
       -video_size 1280x720 \
       -framerate 30 \
       -re \
       -i /dev/video2 \
       -f mjpeg \
       -q:v 3 \
       -an \
       -vf "format=yuvj420p" \
       -fflags +genpts \
       -flags low_delay \
       -strict experimental \
       -listen 1 \
       http://0.0.0.0:$PORT2 &
CAM2_PID=$!

echo "Streams started!"
echo "Camera 1: http://<jetson_ip>:$PORT1"
echo "Camera 2: http://<jetson_ip>:$PORT2"
echo ""
echo "PIDs: Camera1=$CAM1_PID, Camera2=$CAM2_PID"
echo "Press Ctrl+C to stop"

# Wait a moment then test
sleep 2
echo ""
echo "Testing streams..."
curl -I http://localhost:$PORT1 2>&1 | head -3 || echo "Camera 1 not ready yet"
curl -I http://localhost:$PORT2 2>&1 | head -3 || echo "Camera 2 not ready yet"

wait

