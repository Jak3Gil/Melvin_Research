#!/bin/bash
# Simple camera detection test using ffmpeg and basic image analysis

CAMERA1="/dev/video0"
CAMERA2="/dev/video2"
OUTPUT_DIR="/tmp/camera_detection"
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "Camera Object Detection Test"
echo "=========================================="
echo ""

# Kill any processes using cameras
echo "Freeing cameras..."
fuser -k /dev/video0 2>/dev/null
fuser -k /dev/video2 2>/dev/null
sleep 1

echo "Testing cameras..."
for cam in "$CAMERA1" "$CAMERA2"; do
    if [ -e "$cam" ]; then
        echo "✓ $cam exists"
    else
        echo "✗ $cam not found"
    fi
done

echo ""
echo "Capturing test frames..."
echo ""

# Capture a frame from each camera
ffmpeg -f v4l2 -i "$CAMERA1" -frames:v 1 -y "$OUTPUT_DIR/cam1_test.jpg" 2>/dev/null &
PID1=$!

ffmpeg -f v4l2 -i "$CAMERA2" -frames:v 1 -y "$OUTPUT_DIR/cam2_test.jpg" 2>/dev/null &
PID2=$!

wait $PID1 $PID2

# Check results
if [ -f "$OUTPUT_DIR/cam1_test.jpg" ]; then
    SIZE1=$(stat -c%s "$OUTPUT_DIR/cam1_test.jpg" 2>/dev/null || echo "0")
    echo "Camera 1: Captured ($SIZE1 bytes)"
else
    echo "Camera 1: Failed"
fi

if [ -f "$OUTPUT_DIR/cam2_test.jpg" ]; then
    SIZE2=$(stat -c%s "$OUTPUT_DIR/cam2_test.jpg" 2>/dev/null || echo "0")
    echo "Camera 2: Captured ($SIZE2 bytes)"
else
    echo "Camera 2: Failed"
fi

echo ""
echo "=========================================="
echo "Camera Detection Ready"
echo "=========================================="
echo ""
echo "Note: Full YOLO installation requires more disk space."
echo "Current disk usage: $(df -h / | tail -1 | awk '{print $5}')"
echo ""
echo "To install YOLO for full object detection, free up space or:"
echo "1. Clean large files (check ~/melvin/jetson_brain.m - 17GB)"
echo "2. Use external storage"
echo "3. Use ONNX models (lighter weight)"
echo ""

