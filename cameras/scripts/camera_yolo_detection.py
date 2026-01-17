#!/usr/bin/env python3
"""
Real-time Object Detection with YOLOv8 on USB Cameras
Detects objects and prints classifications to terminal
"""

import cv2
import sys
import time
from datetime import datetime

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠ YOLO not installed. Installing now...")
    import subprocess
    result = subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "ultralytics"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        from ultralytics import YOLO
        YOLO_AVAILABLE = True
        print("✓ YOLO installed successfully!")
    else:
        print("✗ Failed to install YOLO")
        print("Error:", result.stderr)
        sys.exit(1)

# Camera devices
CAMERA1 = "/dev/video0"
CAMERA2 = "/dev/video2"

print("="*60)
print("YOLOv8 Object Detection on Cameras")
print("="*60)
print()

# Load YOLOv8 model
print("Loading YOLOv8 model (will download if needed)...")
try:
    model = YOLO('yolov8n.pt')  # nano - smallest, fastest
    print(f"✓ YOLOv8 model loaded!")
    print(f"  Can detect {len(model.names)} object classes")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("Starting detection on cameras...")
print("Press Ctrl+C to stop")
print("="*60 + "\n")

# Open cameras using V4L2 backend (more reliable than GStreamer)
cap1 = cv2.VideoCapture(CAMERA1, cv2.CAP_V4L2)
cap2 = cv2.VideoCapture(CAMERA2, cv2.CAP_V4L2)

# Set camera properties
for cap, name in [(cap1, "Camera 1"), (cap2, "Camera 2")]:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)
    
    if not cap.isOpened():
        print(f"⚠ Warning: {name} could not be opened")
    else:
        print(f"✓ {name} opened successfully")

print()

frame_count = 0
last_print_time = time.time()
print_interval = 2.0  # Print every 2 seconds

try:
    while True:
        frame_count += 1
        current_time = time.time()
        
        # Read frames
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        
        if not ret1 and not ret2:
            time.sleep(0.1)
            continue
        
        detections = {}
        
        # Process Camera 1
        if ret1:
            try:
                results1 = model(frame1, verbose=False, conf=0.5)
                cam1_objects = []
                
                for r in results1:
                    for box in r.boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = model.names[class_id]
                        cam1_objects.append((class_name, confidence))
                
                if cam1_objects:
                    detections["Camera 1"] = cam1_objects
            except Exception as e:
                pass
        
        # Process Camera 2
        if ret2:
            try:
                results2 = model(frame2, verbose=False, conf=0.5)
                cam2_objects = []
                
                for r in results2:
                    for box in r.boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = model.names[class_id]
                        cam2_objects.append((class_name, confidence))
                
                if cam2_objects:
                    detections["Camera 2"] = cam2_objects
            except Exception as e:
                pass
        
        # Print detections
        if current_time - last_print_time >= print_interval:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Frame {frame_count}")
            print("-" * 60)
            
            if detections:
                for camera_name, objects in detections.items():
                    print(f"\n{camera_name}:")
                    
                    # Count occurrences
                    object_counts = {}
                    for obj_name, conf in objects:
                        if obj_name not in object_counts:
                            object_counts[obj_name] = []
                        object_counts[obj_name].append(conf)
                    
                    # Print with counts
                    for obj_name, confidences in sorted(object_counts.items()):
                        count = len(confidences)
                        avg_conf = sum(confidences) / len(confidences)
                        count_str = f" x{count}" if count > 1 else ""
                        print(f"  • {obj_name}{count_str} (confidence: {avg_conf:.1%})")
            else:
                print("No objects detected (confidence > 50%)")
            
            print("-" * 60)
            last_print_time = current_time
        
        time.sleep(0.067)  # ~15 FPS

except KeyboardInterrupt:
    print("\n\nStopping detection...")
finally:
    cap1.release()
    cap2.release()
    print("✓ Cameras released")
    print("Done!")

