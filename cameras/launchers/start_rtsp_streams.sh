#!/bin/bash
# Start RTSP streams - better compatibility with VLC
# RTSP is specifically designed for video streaming

set -e

RTSP_PORT1=8554
RTSP_PORT2=8555

echo "Starting RTSP video streams (best for VLC)..."
echo "Camera 1 on RTSP port $RTSP_PORT1"
echo "Camera 2 on RTSP port $RTSP_PORT2"
echo ""

# Use ffmpeg with RTSP server
# Camera 1
ffmpeg -f v4l2 \
       -input_format mjpeg \
       -video_size 1280x720 \
       -framerate 30 \
       -i /dev/video0 \
       -c:v libx264 \
       -preset ultrafast \
       -tune zerolatency \
       -g 30 \
       -f rtsp \
       rtsp://0.0.0.0:$RTSP_PORT1/stream1 &
CAM1_PID=$!

# Camera 2
ffmpeg -f v4l2 \
       -input_format mjpeg \
       -video_size 1280x720 \
       -framerate 30 \
       -i /dev/video2 \
       -c:v libx264 \
       -preset ultrafast \
       -tune zerolatency \
       -g 30 \
       -f rtsp \
       rtsp://0.0.0.0:$RTSP_PORT2/stream2 &
CAM2_PID=$!

echo "RTSP streams started!"
echo "Camera 1: rtsp://<jetson_ip>:$RTSP_PORT1/stream1"
echo "Camera 2: rtsp://<jetson_ip>:$RTSP_PORT2/stream2"
echo ""
echo "PIDs: Camera1=$CAM1_PID, Camera2=$CAM2_PID"
echo "Press Ctrl+C to stop"

wait

