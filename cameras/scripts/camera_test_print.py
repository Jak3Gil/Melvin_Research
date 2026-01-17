#!/usr/bin/env python3
"""
Simple camera test - prints what cameras see
Uses OpenCV to capture frames and print basic information
"""
import cv2
import numpy as np
import time

def main():
    print("="*60)
    print("Camera Test - Printing Frame Information")
    print("="*60)
    
    # Open cameras
    print("\nOpening cameras...")
    cap1 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(2)
    
    if not cap1.isOpened():
        print("✗ Could not open camera 1 (/dev/video0)")
    else:
        print("✓ Camera 1 opened")
    
    if not cap2.isOpened():
        print("✗ Could not open camera 2 (/dev/video2)")
    else:
        print("✓ Camera 2 opened")
    
    if not cap1.isOpened() and not cap2.isOpened():
        print("\n✗ No cameras available")
        return
    
    print("\nStarting capture (press Ctrl+C to stop)...\n")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            frame_count += 1
            detections = []
            
            # Camera 1
            if cap1.isOpened():
                ret1, frame1 = cap1.read()
                if ret1:
                    h, w = frame1.shape[:2]
                    mean_color = np.mean(frame1, axis=(0, 1))
                    brightness = np.mean(frame1)
                    detections.append(f"Camera 1: {w}x{h}, brightness={brightness:.1f}, RGB=({mean_color[2]:.0f},{mean_color[1]:.0f},{mean_color[0]:.0f})")
            
            # Camera 2
            if cap2.isOpened():
                ret2, frame2 = cap2.read()
                if ret2:
                    h, w = frame2.shape[:2]
                    mean_color = np.mean(frame2, axis=(0, 1))
                    brightness = np.mean(frame2)
                    detections.append(f"Camera 2: {w}x{h}, brightness={brightness:.1f}, RGB=({mean_color[2]:.0f},{mean_color[1]:.0f},{mean_color[0]:.0f})")
            
            # Print every 30 frames (~1 second at 30fps)
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"\n[Frame {frame_count}, FPS: {fps:.1f}]")
                for det in detections:
                    print(f"  {det}")
                print()
            
            time.sleep(0.01)  # Small delay
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        cap1.release()
        cap2.release()
        print("Cameras closed")

if __name__ == "__main__":
    main()

