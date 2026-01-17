#!/usr/bin/env python3
"""
Real-time Object Detection using YOLOv8 on USB Cameras
Detects objects from both cameras and prints results to terminal
"""

import cv2
from ultralytics import YOLO
import time
from datetime import datetime

# Camera devices
CAMERA1 = "/dev/video0"
CAMERA2 = "/dev/video2"

# Initialize YOLOv8 model (will auto-download if not present)
print("Loading YOLOv8 model...")
try:
    model = YOLO('yolov8n.pt')  # nano model - fastest, good for Jetson
    print("✓ YOLOv8 model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Trying to download model...")
    model = YOLO('yolov8n.pt')
    print("✓ Model downloaded and loaded!")

print(f"\nModel classes: {len(model.names)} objects")
print(f"Sample classes: {list(model.names.values())[:10]}...")
print("\n" + "="*60)
print("Starting object detection on cameras...")
print("Press Ctrl+C to stop")
print("="*60 + "\n")

# Open cameras
cap1 = cv2.VideoCapture(CAMERA1)
cap2 = cv2.VideoCapture(CAMERA2)

# Set camera properties
for cap, name in [(cap1, "Camera 1"), (cap2, "Camera 2")]:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print(f"⚠ Warning: {name} ({CAMERA1 if cap == cap1 else CAMERA2}) could not be opened")
    else:
        print(f"✓ {name} opened successfully")

print()

frame_count = 0
last_print_time = time.time()
print_interval = 2.0  # Print detections every 2 seconds

try:
    while True:
        frame_count += 1
        current_time = time.time()
        
        # Read frames from both cameras
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        
        if not ret1 and not ret2:
            print("⚠ Both cameras failed to read frames")
            time.sleep(0.1)
            continue
        
        detections = {}
        
        # Process Camera 1
        if ret1:
            results1 = model(frame1, verbose=False)
            cam1_objects = []
            for r in results1:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = model.names[class_id]
                    
                    if confidence > 0.5:  # Only show detections with >50% confidence
                        cam1_objects.append((class_name, confidence))
            
            if cam1_objects:
                detections["Camera 1"] = cam1_objects
        
        # Process Camera 2
        if ret2:
            results2 = model(frame2, verbose=False)
            cam2_objects = []
            for r in results2:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = model.names[class_id]
                    
                    if confidence > 0.5:  # Only show detections with >50% confidence
                        cam2_objects.append((class_name, confidence))
            
            if cam2_objects:
                detections["Camera 2"] = cam2_objects
        
        # Print detections every N seconds
        if current_time - last_print_time >= print_interval:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Frame {frame_count}")
            print("-" * 60)
            
            if detections:
                for camera_name, objects in detections.items():
                    print(f"\n{camera_name}:")
                    
                    # Count occurrences of each object type
                    object_counts = {}
                    for obj_name, conf in objects:
                        if obj_name not in object_counts:
                            object_counts[obj_name] = []
                        object_counts[obj_name].append(conf)
                    
                    # Print each detected object with count and average confidence
                    for obj_name, confidences in sorted(object_counts.items()):
                        count = len(confidences)
                        avg_conf = sum(confidences) / len(confidences)
                        count_str = f" x{count}" if count > 1 else ""
                        print(f"  • {obj_name}{count_str} (confidence: {avg_conf:.1%})")
            else:
                print("No objects detected")
            
            print("-" * 60)
            last_print_time = current_time
        
        # Small delay to prevent excessive CPU usage
        time.sleep(0.033)  # ~30 FPS

except KeyboardInterrupt:
    print("\n\nStopping object detection...")
finally:
    cap1.release()
    cap2.release()
    print("✓ Cameras released")
    print("Done!")

