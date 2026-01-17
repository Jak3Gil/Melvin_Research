#!/usr/bin/env python3
"""
Simple camera test - uses fswebcam to capture images and prints basic info
Works around OpenCV memory issues by using command-line tools
"""

import subprocess
import time
import os
from datetime import datetime

CAMERA1 = "/dev/video0"
CAMERA2 = "/dev/video2"
OUTPUT_DIR = "/tmp/camera_test"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*60)
print("Simple Camera Test - Checking what cameras see")
print("="*60)
print()

# Check if cameras exist
for cam, name in [(CAMERA1, "Camera 1"), (CAMERA2, "Camera 2")]:
    if os.path.exists(cam):
        print(f"✓ {name} ({cam}) exists")
    else:
        print(f"✗ {name} ({cam}) not found")

print()

# Use fswebcam if available, otherwise use ffmpeg
if subprocess.run(["which", "fswebcam"], capture_output=True).returncode == 0:
    print("Using fswebcam to capture images...")
    capture_tool = "fswebcam"
elif subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0:
    print("Using ffmpeg to capture images...")
    capture_tool = "ffmpeg"
else:
    print("Error: Neither fswebcam nor ffmpeg found!")
    exit(1)

print(f"\nCapturing frames every 3 seconds...")
print("Press Ctrl+C to stop\n")

frame_count = 0

try:
    while True:
        frame_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        for cam, name in [(CAMERA1, "Camera 1"), (CAMERA2, "Camera 2")]:
            output_file = f"{OUTPUT_DIR}/{name.lower().replace(' ', '_')}_{frame_count}.jpg"
            
            if capture_tool == "fswebcam":
                cmd = ["fswebcam", "-d", cam, "-r", "640x480", "--no-banner", output_file]
            else:  # ffmpeg
                cmd = ["ffmpeg", "-f", "v4l2", "-i", cam, "-frames:v", "1", "-y", output_file]
            
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            
            if result.returncode == 0 and os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"[{timestamp}] {name}: Captured frame {frame_count} ({size} bytes)")
            else:
                print(f"[{timestamp}] {name}: Failed to capture")
        
        print("-" * 60)
        time.sleep(3)

except KeyboardInterrupt:
    print("\n\nStopping...")
    print(f"\nCaptured {frame_count} frames")
    print(f"Images saved to: {OUTPUT_DIR}")
    print("Done!")

