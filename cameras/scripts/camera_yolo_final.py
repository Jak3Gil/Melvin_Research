#!/usr/bin/env python3
"""
Real-time Object Detection using YOLOv8 ONNX Runtime
Detects objects from both cameras and prints to terminal
"""

import cv2
import numpy as np
import onnxruntime as ort
import time
from datetime import datetime
import os
import subprocess

# COCO class names (80 objects)
COCO_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
    'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
    'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
    'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
    'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
    'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
    'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
    'toothbrush'
]

# Try multiple locations for model
MODEL_PATHS = [
    "/tmp/yolov8n.onnx",
    "/mnt/melvin_ssd/yolov8n.onnx",
    os.path.expanduser("~/yolov8n.onnx")
]
MODEL_PATH = "/tmp/yolov8n.onnx"  # Default
MODEL_URL = "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.onnx"

def download_model():
    """Download YOLOv8n ONNX model using wget or curl"""
    global MODEL_PATH
    
    # Check all possible locations first
    for path in MODEL_PATHS:
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 1000000:
                MODEL_PATH = path
                print(f"✓ Model found at {path} ({size/1024/1024:.1f}MB)")
                return True
    
    # Try to download to SSD first (more space)
    if os.path.exists("/mnt/melvin_ssd"):
        download_path = "/mnt/melvin_ssd/yolov8n.onnx"
    else:
        download_path = MODEL_PATH
    
    print(f"Downloading YOLOv8n ONNX model (~6MB) to {download_path}...")
    
    # Try wget first
    result = subprocess.run(["wget", "-q", "--show-progress", "-O", download_path, MODEL_URL], 
                          capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(download_path):
        size = os.path.getsize(download_path)
        if size > 1000000:
            MODEL_PATH = download_path
            # Create symlink in /tmp for convenience
            if download_path != "/tmp/yolov8n.onnx":
                try:
                    os.symlink(download_path, "/tmp/yolov8n.onnx")
                except:
                    pass
            print(f"✓ Model downloaded ({size/1024/1024:.1f}MB)")
            return True
    
    # Try curl
    result = subprocess.run(["curl", "-L", "-o", download_path, MODEL_URL],
                          capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(download_path):
        size = os.path.getsize(download_path)
        if size > 1000000:
            MODEL_PATH = download_path
            if download_path != "/tmp/yolov8n.onnx":
                try:
                    os.symlink(download_path, "/tmp/yolov8n.onnx")
                except:
                    pass
            print(f"✓ Model downloaded ({size/1024/1024:.1f}MB)")
            return True
    
    print("✗ Failed to download model")
    return False

def prepare_input(frame, size=(640, 640)):
    """Prepare frame for YOLO"""
    img = cv2.resize(frame, size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    return np.expand_dims(img, axis=0)

def parse_outputs(output, conf_threshold=0.5):
    """Parse YOLO output"""
    detections = []
    try:
        # Output shape: [1, 84, 8400] for YOLOv8
        output = output[0]  # Remove batch dimension
        if len(output.shape) == 3:
            output = np.transpose(output, (1, 2, 0))  # [8400, 84]
        
        for pred in output[:2000]:  # Process first 2000 predictions
            if len(pred) < 84:
                continue
            
            scores = pred[4:84]
            class_id = np.argmax(scores)
            confidence = float(scores[class_id])
            
            if confidence > conf_threshold and class_id < len(COCO_CLASSES):
                detections.append((COCO_CLASSES[class_id], confidence))
    except:
        pass
    return detections

# Main
print("="*60)
print("YOLOv8 Object Detection")
print("="*60)

if not download_model():
    print("\nCannot proceed without model. Trying to free space...")
    print("Current disk: 100% full")
    print("\nPlease free up space or download model manually:")
    print(f"  wget {MODEL_URL} -O {MODEL_PATH}")
    exit(1)

print("\nLoading ONNX model...")
try:
    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    print(f"✓ Model loaded!")
    print(f"  Detecting {len(COCO_CLASSES)} object classes")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

print("\n" + "="*60)
print("Starting detection...")
print("Press Ctrl+C to stop")
print("="*60 + "\n")

cap1 = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
cap2 = cv2.VideoCapture("/dev/video2", cv2.CAP_V4L2)

for cap, name in [(cap1, "Camera 1"), (cap2, "Camera 2")]:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print(f"✓ {name} ready" if cap.isOpened() else f"✗ {name} failed")

frame = 0
last_print = time.time()

try:
    while True:
        frame += 1
        ret1, f1 = cap1.read()
        ret2, f2 = cap2.read()
        
        detections = {}
        
        if ret1:
            try:
                inp = prepare_input(f1)
                out = session.run([output_name], {input_name: inp})
                objs = parse_outputs(out)
                if objs:
                    detections["Camera 1"] = objs
            except:
                pass
        
        if ret2:
            try:
                inp = prepare_input(f2)
                out = session.run([output_name], {input_name: inp})
                objs = parse_outputs(out)
                if objs:
                    detections["Camera 2"] = objs
            except:
                pass
        
        if time.time() - last_print >= 2.0:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{ts}] Frame {frame}")
            print("-" * 60)
            
            if detections:
                for cam, objs in detections.items():
                    print(f"\n{cam}:")
                    counts = {}
                    for name, conf in objs:
                        if name not in counts:
                            counts[name] = []
                        counts[name].append(conf)
                    
                    for name, confs in sorted(counts.items()):
                        n = len(confs)
                        avg = sum(confs) / n
                        print(f"  • {name}{f' x{n}' if n > 1 else ''} ({avg:.1%})")
            else:
                print("No objects detected")
            
            print("-" * 60)
            last_print = time.time()
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nStopping...")
finally:
    cap1.release()
    cap2.release()
    print("Done!")

