#!/bin/bash
# Test camera 2 directly

echo "Testing camera 2..."
ffmpeg -f v4l2 \
       -fflags nobuffer \
       -flags low_delay \
       -strict experimental \
       -input_format mjpeg \
       -video_size 1280x720 \
       -framerate 30 \
       -probesize 32 \
       -analyzeduration 0 \
       -i /dev/video2 \
       -f mjpeg \
       -frames:v 5 \
       -y /tmp/cam2_test_%02d.jpg 2>&1 | tail -20

if [ -f /tmp/cam2_test_01.jpg ]; then
    echo "SUCCESS: Camera 2 captured images"
    ls -lh /tmp/cam2_test_*.jpg
else
    echo "FAILED: Camera 2 did not capture images"
fi

