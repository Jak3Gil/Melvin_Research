#!/bin/bash
# Capture images from both USB cameras on Jetson

set -e

OUTPUT_DIR="$HOME/camera_captures"
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "USB Camera Capture Script"
echo "=========================================="
echo ""

# Check if cameras exist
if [ ! -e /dev/video0 ]; then
    echo "Error: Camera 1 (/dev/video0) not found"
    exit 1
fi

if [ ! -e /dev/video2 ]; then
    echo "Error: Camera 2 (/dev/video2) not found"
    exit 1
fi

echo "Detected cameras:"
echo "  Camera 1: /dev/video0"
echo "  Camera 2: /dev/video2"
echo ""

# Try fswebcam first (simpler)
if command -v fswebcam &> /dev/null; then
    echo "Using fswebcam to capture images..."
    
    # Capture from camera 1
    echo "Capturing from Camera 1..."
    fswebcam -d /dev/video0 -r 1280x720 --no-banner "$OUTPUT_DIR/camera1.jpg" 2>&1 || {
        echo "Trying camera 1 with lower resolution..."
        fswebcam -d /dev/video0 -r 640x480 --no-banner "$OUTPUT_DIR/camera1.jpg" 2>&1
    }
    
    # Capture from camera 2
    echo "Capturing from Camera 2..."
    fswebcam -d /dev/video2 -r 1280x720 --no-banner "$OUTPUT_DIR/camera2.jpg" 2>&1 || {
        echo "Trying camera 2 with lower resolution..."
        fswebcam -d /dev/video2 -r 640x480 --no-banner "$OUTPUT_DIR/camera2.jpg" 2>&1
    }
    
elif command -v v4l2-ctl &> /dev/null && command -v ffmpeg &> /dev/null; then
    echo "Using v4l2-ctl and ffmpeg to capture images..."
    
    # Capture from camera 1
    echo "Capturing from Camera 1..."
    ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -i /dev/video0 -frames:v 1 -y "$OUTPUT_DIR/camera1.jpg" 2>&1 || \
    ffmpeg -f v4l2 -input_format yuyv422 -video_size 640x480 -i /dev/video0 -frames:v 1 -y "$OUTPUT_DIR/camera1.jpg" 2>&1
    
    # Capture from camera 2
    echo "Capturing from Camera 2..."
    ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -i /dev/video2 -frames:v 1 -y "$OUTPUT_DIR/camera2.jpg" 2>&1 || \
    ffmpeg -f v4l2 -input_format yuyv422 -video_size 640x480 -i /dev/video2 -frames:v 1 -y "$OUTPUT_DIR/camera2.jpg" 2>&1
    
else
    echo "Error: No capture tool found. Installing fswebcam..."
    sudo apt-get update
    sudo apt-get install -y fswebcam
    echo "Please run this script again."
    exit 1
fi

# Verify images were created
if [ -f "$OUTPUT_DIR/camera1.jpg" ] && [ -f "$OUTPUT_DIR/camera2.jpg" ]; then
    echo ""
    echo "=========================================="
    echo "Success! Images captured:"
    echo "  Camera 1: $OUTPUT_DIR/camera1.jpg"
    echo "  Camera 2: $OUTPUT_DIR/camera2.jpg"
    echo "=========================================="
    
    # Show file sizes
    ls -lh "$OUTPUT_DIR"/camera*.jpg
else
    echo "Error: Failed to capture one or both images"
    exit 1
fi

