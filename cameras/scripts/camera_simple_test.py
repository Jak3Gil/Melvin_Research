#!/usr/bin/env python3
"""
Simple camera test - captures from both cameras and prints image stats
No AI required - just verifies cameras work
"""
import cv2
import time
from datetime import datetime

print("="*60)
print("Camera Test - No AI")
print("="*60)

cap1 = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
cap2 = cv2.VideoCapture("/dev/video2", cv2.CAP_V4L2)

for cap, name in [(cap1, "Camera 1"), (cap2, "Camera 2")]:
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print(f"✓ {name} ready")
    else:
        print(f"✗ {name} failed to open")

print("\n" + "="*60)
print("Starting capture...")
print("Press Ctrl+C to stop")
print("="*60 + "\n")

frame = 0

try:
    while True:
        frame += 1
        ret1, f1 = cap1.read()
        ret2, f2 = cap2.read()
        
        if time.time() % 2 < 0.1:  # Print every ~2 seconds
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{ts}] Frame {frame}")
            print("-" * 60)
            
            if ret1:
                h, w = f1.shape[:2]
                mean = f1.mean()
                print(f"Camera 1: {w}x{h}, mean brightness: {mean:.1f}")
            else:
                print("Camera 1: No frame")
            
            if ret2:
                h, w = f2.shape[:2]
                mean = f2.mean()
                print(f"Camera 2: {w}x{h}, mean brightness: {mean:.1f}")
            else:
                print("Camera 2: No frame")
            
            print("-" * 60)
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nStopping...")
finally:
    cap1.release()
    cap2.release()
    print("Done!")

