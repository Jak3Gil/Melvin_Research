#!/bin/bash
# Stream both USB cameras from Jetson to local machine
# This script runs on the Jetson

CAMERA1="/dev/video0"
CAMERA2="/dev/video2"
WIDTH=640
HEIGHT=480
FPS=30

PORT1=8080
PORT2=8081

echo "Starting camera streams..."
echo "Camera 1: http://192.168.1.119:$PORT1"
echo "Camera 2: http://192.168.1.119:$PORT2"
echo ""
echo "Press Ctrl+C to stop all streams"

# Stream Camera 1
ffmpeg -f v4l2 -video_size ${WIDTH}x${HEIGHT} -framerate $FPS -i $CAMERA1 \
    -f mjpeg -qscale 2 -listen 1 -timeout 60 http://0.0.0.0:$PORT1/ > /tmp/cam1.log 2>&1 &
PID1=$!

# Stream Camera 2
ffmpeg -f v4l2 -video_size ${WIDTH}x${HEIGHT} -framerate $FPS -i $CAMERA2 \
    -f mjpeg -qscale 2 -listen 1 -timeout 60 http://0.0.0.0:$PORT2/ > /tmp/cam2.log 2>&1 &
PID2=$!

echo "Streams started (PIDs: $PID1, $PID2)"
echo ""

# Wait for user interrupt
trap "kill $PID1 $PID2 2>/dev/null; exit" INT TERM

wait

