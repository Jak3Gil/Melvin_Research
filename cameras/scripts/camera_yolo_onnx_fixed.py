#!/usr/bin/env python3
"""
Real-time Object Detection using ONNX Runtime with YOLOv8 ONNX model
Downloads model from correct source
"""

import cv2
import numpy as np
import onnxruntime as ort
import time
from datetime import datetime
import os
import urllib.request
import sys

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

MODEL_PATH = "/tmp/yolov8n.onnx"
# Alternative model sources - try ONNX Model Zoo YOLOv8
MODEL_URLS = [
    "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.onnx",
    "https://github.com/onnx/models/raw/main/validated/vision/object_detection_segmentation/yolov8/dependencies/yolov8n.onnx",
]

def download_model():
    """Download YOLOv8n ONNX model"""
    if os.path.exists(MODEL_PATH):
        size = os.path.getsize(MODEL_PATH)
        if size > 1000000:  # At least 1MB
            print(f"✓ Model found at {MODEL_PATH} ({size/1024/1024:.1f}MB)")
            return True
    
    print(f"Downloading YOLOv8n ONNX model...")
    
    # Try to get model via wget/curl first (more reliable)
    for url in MODEL_URLS:
        print(f"  Trying: {url}")
        result = os.system(f"wget -q --show-progress -O {MODEL_PATH} '{url}' 2>&1")
        if result == 0 and os.path.exists(MODEL_PATH):
            size = os.path.getsize(MODEL_PATH)
            if size > 1000000:
                print(f"✓ Model downloaded ({size/1024/1024:.1f}MB)")
                return True
    
    # Fallback: use Python urllib
    for url in MODEL_URLS:
        try:
            print(f"  Trying Python download: {url}")
            urllib.request.urlretrieve(url, MODEL_PATH)
            if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 1000000:
                print(f"✓ Model downloaded")
                return True
        except Exception as e:
            print(f"    Failed: {e}")
            continue
    
    print("✗ Could not download model from any source")
    print("\nTrying to use a simpler classification approach...")
    return False

def prepare_input(frame, input_size=(640, 640)):
    """Prepare frame for YOLO input"""
    img_resized = cv2.resize(frame, input_size)
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_normalized = img_rgb.astype(np.float32) / 255.0
    img_transposed = np.transpose(img_normalized, (2, 0, 1))
    img_batch = np.expand_dims(img_transposed, axis=0)
    return img_batch

def parse_outputs(outputs, conf_threshold=0.5):
    """Parse YOLO outputs and extract detections"""
    detections = []
    
    try:
        output = outputs[0]  # Shape: [1, 84, 8400] or similar
        predictions = np.transpose(output, (0, 2, 1))[0] if len(output.shape) == 3 else output[0]
        
        for pred in predictions[:1000]:  # Limit processing
            if len(pred) < 84:
                continue
                
            x_center, y_center, width, height = pred[:4]
            scores = pred[4:84] if len(pred) >= 84 else pred[4:]
            
            if len(scores) < len(COCO_CLASSES):
                continue
                
            class_id = np.argmax(scores)
            confidence = scores[class_id] if class_id < len(scores) else 0
            
            if confidence > conf_threshold and class_id < len(COCO_CLASSES):
                class_name = COCO_CLASSES[class_id]
                detections.append((class_name, float(confidence)))
    except Exception as e:
        pass
    
    return detections

# Camera devices
CAMERA1 = "/dev/video0"
CAMERA2 = "/dev/video2"

print("="*60)
print("YOLOv8 Object Detection (ONNX Runtime)")
print("="*60)
print()

# Download model
model_available = download_model()

if not model_available:
    print("\nUsing simplified detection (no model - will show camera status only)")
    print("To get full YOLO detection:")
    print("  1. Free up disk space (currently 100% full)")
    print("  2. Manually download YOLOv8 ONNX model")
    print("  3. Or install ultralytics package")
    
    # Fallback: just show camera status
    cap1 = cv2.VideoCapture(CAMERA1, cv2.CAP_V4L2)
    cap2 = cv2.VideoCapture(CAMERA2, cv2.CAP_V4L2)
    
    try:
        while True:
            ret1, _ = cap1.read()
            ret2, _ = cap2.read()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Camera 1: {'Active' if ret1 else 'Inactive'}, Camera 2: {'Active' if ret2 else 'Inactive'}")
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        cap1.release()
        cap2.release()
    sys.exit(0)

# Load ONNX model
print("Loading ONNX model...")
try:
    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    output_names = [output.name for output in session.get_outputs()]
    input_shape = session.get_inputs()[0].shape
    input_size = (input_shape[3], input_shape[2])  # (width, height)
    
    print(f"✓ Model loaded!")
    print(f"  Input: {input_name}, Size: {input_size}")
    print(f"  Can detect {len(COCO_CLASSES)} object classes")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("Starting detection on cameras...")
print("Press Ctrl+C to stop")
print("="*60 + "\n")

# Open cameras
cap1 = cv2.VideoCapture(CAMERA1, cv2.CAP_V4L2)
cap2 = cv2.VideoCapture(CAMERA2, cv2.CAP_V4L2)

for cap, name in [(cap1, "Camera 1"), (cap2, "Camera 2")]:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 10)
    
    if not cap.isOpened():
        print(f"⚠ Warning: {name} could not be opened")
    else:
        print(f"✓ {name} opened successfully")

print()

frame_count = 0
last_print_time = time.time()
print_interval = 2.0

try:
    while True:
        frame_count += 1
        current_time = time.time()
        
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        
        if not ret1 and not ret2:
            time.sleep(0.1)
            continue
        
        detections = {}
        
        # Process Camera 1
        if ret1:
            try:
                input_data = prepare_input(frame1, input_size)
                outputs = session.run(output_names, {input_name: input_data})
                objects = parse_outputs(outputs, conf_threshold=0.5)
                if objects:
                    detections["Camera 1"] = objects
            except Exception as e:
                pass
        
        # Process Camera 2
        if ret2:
            try:
                input_data = prepare_input(frame2, input_size)
                outputs = session.run(output_names, {input_name: input_data})
                objects = parse_outputs(outputs, conf_threshold=0.5)
                if objects:
                    detections["Camera 2"] = objects
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
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nStopping detection...")
finally:
    cap1.release()
    cap2.release()
    print("✓ Cameras released")
    print("Done!")

