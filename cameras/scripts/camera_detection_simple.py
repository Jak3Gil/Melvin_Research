#!/usr/bin/env python3
"""
Simple object detection using OpenCV DNN with MobileNet-SSD
This model is lightweight and easier to download
"""
import cv2
import numpy as np
import subprocess
import os
import sys

# COCO class names for MobileNet-SSD (20 classes)
CLASSES = [
    'background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
    'car', 'cat', 'chair', 'cow', 'dining table', 'dog', 'horse', 'motorbike',
    'person', 'potted plant', 'sheep', 'sofa', 'train', 'tv/monitor'
]

# Model files
MODEL_URL = "https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel"
CONFIG_URL = "https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.prototxt"
MODEL_PATH = "/tmp/MobileNetSSD.caffemodel"
CONFIG_PATH = "/tmp/MobileNetSSD.prototxt"

def download_file(url, dest):
    """Download file using wget or curl"""
    if os.path.exists(dest):
        size = os.path.getsize(dest)
        if size > 1000:
            print(f"✓ Found {dest} ({size/1024/1024:.1f}MB)")
            return True
    
    print(f"Downloading {os.path.basename(dest)}...")
    # Try wget
    result = subprocess.run(["wget", "-q", "--show-progress", "-O", dest, url],
                          capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 1000:
        print(f"✓ Downloaded ({os.path.getsize(dest)/1024/1024:.1f}MB)")
        return True
    
    # Try curl
    result = subprocess.run(["curl", "-L", "-o", dest, url],
                          capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 1000:
        print(f"✓ Downloaded ({os.path.getsize(dest)/1024/1024:.1f}MB)")
        return True
    
    return False

def main():
    print("="*60)
    print("Camera Object Detection (MobileNet-SSD)")
    print("="*60)
    
    # Download model files
    if not download_file(CONFIG_URL, CONFIG_PATH):
        print("✗ Failed to download config file")
        return
    if not download_file(MODEL_URL, MODEL_PATH):
        print("✗ Failed to download model file")
        return
    
    # Load DNN model
    print("Loading model...")
    net = cv2.dnn.readNetFromCaffe(CONFIG_PATH, MODEL_PATH)
    print("✓ Model loaded")
    
    # Open cameras
    print("\nOpening cameras...")
    cap1 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(2)
    
    if not cap1.isOpened():
        print("✗ Could not open camera 1 (/dev/video0)")
        return
    if not cap2.isOpened():
        print("✗ Could not open camera 2 (/dev/video2)")
        return
    
    print("✓ Cameras opened")
    print("\nStarting detection (press Ctrl+C to stop)...\n")
    
    frame_count = 0
    try:
        while True:
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()
            
            if not ret1 and not ret2:
                continue
            
            frame_count += 1
            if frame_count % 30 == 0:  # Print every 30 frames
                detections = []
                
                for idx, (ret, frame, name) in enumerate([(ret1, frame1, "Camera 1"), 
                                                          (ret2, frame2, "Camera 2")], 1):
                    if not ret:
                        continue
                    
                    # Prepare blob
                    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
                    net.setInput(blob)
                    dets = net.forward()
                    
                    # Parse detections
                    h, w = frame.shape[:2]
                    frame_detections = []
                    
                    for i in range(dets.shape[2]):
                        confidence = dets[0, 0, i, 2]
                        if confidence > 0.5:
                            class_id = int(dets[0, 0, i, 1])
                            if class_id < len(CLASSES):
                                frame_detections.append((CLASSES[class_id], confidence))
                    
                    # Print detections
                    if frame_detections:
                        unique_detections = {}
                        for obj, conf in frame_detections:
                            if obj not in unique_detections or conf > unique_detections[obj]:
                                unique_detections[obj] = conf
                        
                        print(f"{name}: {', '.join([f'{obj} ({conf:.2f})' for obj, conf in sorted(unique_detections.items())])}")
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        cap1.release()
        cap2.release()
        print("Cameras closed")

if __name__ == "__main__":
    main()

