#!/bin/bash
# Start HTTP video streams using ffmpeg directly
# Most reliable method for video streaming

set -e

PORT1=8081
PORT2=8082

echo "Starting HTTP video streams..."
echo "Camera 1 on port $PORT1"
echo "Camera 2 on port $PORT2"
echo ""

# Start Camera 1 HTTP stream
ffmpeg -f v4l2 \
       -input_format mjpeg \
       -video_size 1280x720 \
       -framerate 30 \
       -i /dev/video0 \
       -f mjpeg \
       -q:v 3 \
       -listen 1 \
       -timeout 30 \
       http://0.0.0.0:$PORT1 &
CAM1_PID=$!

# Start Camera 2 HTTP stream  
ffmpeg -f v4l2 \
       -input_format mjpeg \
       -video_size 1280x720 \
       -framerate 30 \
       -i /dev/video2 \
       -f mjpeg \
       -q:v 3 \
       -listen 1 \
       -timeout 30 \
       http://0.0.0.0:$PORT2 &
CAM2_PID=$!

echo "Streams started!"
echo "Camera 1: http://<jetson_ip>:$PORT1"
echo "Camera 2: http://<jetson_ip>:$PORT2"
echo ""
echo "PIDs: Camera1=$CAM1_PID, Camera2=$CAM2_PID"
echo "Press Ctrl+C to stop"

wait

