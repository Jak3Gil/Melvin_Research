#!/bin/bash
# Start video streams for both cameras
# Uses RTSP or UDP for low-latency video streaming

set -e

PORT1=8554
PORT2=8555
UDP_PORT1=5004
UDP_PORT2=5005

echo "=========================================="
echo "Starting Video Streams"
echo "=========================================="
echo ""

# Method 1: UDP streams (lowest latency)
start_udp_stream() {
    local device=$1
    local port=$2
    local name=$3
    
    echo "Starting UDP stream for $name on port $port..."
    ffmpeg -f v4l2 \
           -input_format mjpeg \
           -video_size 1280x720 \
           -framerate 30 \
           -i "$device" \
           -c:v libx264 \
           -preset ultrafast \
           -tune zerolatency \
           -g 30 \
           -f mpegts \
           udp://0.0.0.0:$port &
    
    echo "  Stream URL: udp://@:$port"
}

# Method 2: RTSP streams (better compatibility)
start_rtsp_stream() {
    local device=$1
    local port=$2
    local name=$3
    
    echo "Starting RTSP stream for $name on port $port..."
    ffmpeg -f v4l2 \
           -input_format mjpeg \
           -video_size 1280x720 \
           -framerate 30 \
           -i "$device" \
           -c:v libx264 \
           -preset ultrafast \
           -tune zerolatency \
           -g 30 \
           -f rtsp \
           rtsp://0.0.0.0:$port/stream &
    
    echo "  Stream URL: rtsp://<jetson_ip>:$port/stream"
}

# Method 3: HTTP MJPEG stream (simplest)
start_http_mjpeg() {
    local device=$1
    local port=$2
    local name=$3
    
    echo "Starting HTTP MJPEG stream for $name on port $port..."
    # Use Python server for this
    python3 ~/camera_stream_server.py $port &
    echo "  Stream URL: http://<jetson_ip>:$port/stream1.mjpg"
}

# Start UDP streams (lowest latency, works with VLC)
start_udp_stream /dev/video0 $UDP_PORT1 "Camera 1"
start_udp_stream /dev/video2 $UDP_PORT2 "Camera 2"

echo ""
echo "Streams started!"
echo ""
echo "To view in VLC:"
echo "  Camera 1: Media > Open Network Stream > udp://@:5004"
echo "  Camera 2: Media > Open Network Stream > udp://@:5005"
echo ""
echo "Or from command line:"
echo "  vlc udp://@:5004"
echo "  vlc udp://@:5005"
echo ""
echo "Press Ctrl+C to stop all streams"

wait

