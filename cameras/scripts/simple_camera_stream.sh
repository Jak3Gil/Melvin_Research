#!/bin/bash
# Simple direct camera streaming using ffmpeg
# Streams directly without HTTP server

CAMERA1="/dev/video0"
CAMERA2="/dev/video2"
OUTPUT_DIR="$HOME/camera_streams"
mkdir -p "$OUTPUT_DIR"

echo "Starting simple camera streaming..."
echo "Camera 1: $CAMERA1"
echo "Camera 2: $CAMERA2"
echo ""

# Stream camera 1 to file (continuously overwriting)
ffmpeg -f v4l2 \
       -input_format mjpeg \
       -video_size 1280x720 \
       -framerate 30 \
       -i "$CAMERA1" \
       -f image2 \
       -update 1 \
       -y \
       "$OUTPUT_DIR/camera1.jpg" &

CAM1_PID=$!
echo "Camera 1 streaming (PID: $CAM1_PID)"

# Stream camera 2 to file (continuously overwriting)
ffmpeg -f v4l2 \
       -input_format mjpeg \
       -video_size 1280x720 \
       -framerate 30 \
       -i "$CAMERA2" \
       -f image2 \
       -update 1 \
       -y \
       "$OUTPUT_DIR/camera2.jpg" &

CAM2_PID=$!
echo "Camera 2 streaming (PID: $CAM2_PID)"

echo ""
echo "Streams running. Files updating at:"
echo "  $OUTPUT_DIR/camera1.jpg"
echo "  $OUTPUT_DIR/camera2.jpg"
echo ""
echo "Press Ctrl+C to stop"

wait

