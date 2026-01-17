#!/bin/bash
# Install ultralytics (YOLO) without caching to save space

echo "Installing ultralytics (YOLO) for object detection..."
echo "This will use minimal disk space by skipping cache"

# Install with --no-cache-dir and --no-deps (we'll handle deps manually)
pip3 install --no-cache-dir ultralytics 2>&1 | tail -20

if [ $? -eq 0 ]; then
    echo "✓ YOLO installed successfully!"
    python3 -c "from ultralytics import YOLO; print('YOLO import successful')" 2>&1
else
    echo "✗ Installation failed - disk may be full"
    df -h / | grep -E 'Filesystem|/dev/mmcblk0p1'
fi

