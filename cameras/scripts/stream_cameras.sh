#!/bin/bash
# Continuous camera stream capture script
# Captures images from both cameras periodically

set -e

OUTPUT_DIR="$HOME/camera_captures"
mkdir -p "$OUTPUT_DIR"

INTERVAL=${1:-2}  # Default 2 seconds between captures
MAX_CAPTURES=${2:-0}  # 0 = infinite

echo "=========================================="
echo "USB Camera Stream Capture"
echo "=========================================="
echo "Interval: $INTERVAL seconds"
echo "Output: $OUTPUT_DIR"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

capture_count=0

while true; do
    timestamp=$(date +%Y%m%d_%H%M%S)
    camera1_file="$OUTPUT_DIR/camera1_${timestamp}.jpg"
    camera2_file="$OUTPUT_DIR/camera2_${timestamp}.jpg"
    
    # Capture from both cameras
    fswebcam -d /dev/video0 -r 1280x720 --no-banner "$camera1_file" 2>/dev/null || \
    fswebcam -d /dev/video0 -r 640x480 --no-banner "$camera1_file" 2>/dev/null
    
    fswebcam -d /dev/video2 -r 1280x720 --no-banner "$camera2_file" 2>/dev/null || \
    fswebcam -d /dev/video2 -r 640x480 --no-banner "$camera2_file" 2>/dev/null
    
    capture_count=$((capture_count + 1))
    echo "[$capture_count] Captured at $(date '+%H:%M:%S') - Camera1: $(basename $camera1_file), Camera2: $(basename $camera2_file)"
    
    # Keep only latest files for easy access
    cp "$camera1_file" "$OUTPUT_DIR/camera1.jpg"
    cp "$camera2_file" "$OUTPUT_DIR/camera2.jpg"
    
    if [ $MAX_CAPTURES -gt 0 ] && [ $capture_count -ge $MAX_CAPTURES ]; then
        break
    fi
    
    sleep $INTERVAL
done

echo ""
echo "Capture complete. Latest images:"
echo "  $OUTPUT_DIR/camera1.jpg"
echo "  $OUTPUT_DIR/camera2.jpg"

