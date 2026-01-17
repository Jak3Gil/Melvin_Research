#!/usr/bin/env python3
"""
Real-time Object Detection using ONNX Runtime with YOLOv8 ONNX model
Works with existing ONNX Runtime installation - no new packages needed!
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
MODEL_URL = "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.onnx"

def download_model():
    """Download YOLOv8n ONNX model"""
    if os.path.exists(MODEL_PATH):
        size = os.path.getsize(MODEL_PATH)
        if size > 1000000:  # At least 1MB
            print(f"✓ Model found at {MODEL_PATH} ({size/1024/1024:.1f}MB)")
            return True
    
    print(f"Downloading YOLOv8n ONNX model (~6MB)...")
    try:
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            sys.stdout.write(f"\r  Progress: {percent:.1f}%")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, reporthook=show_progress)
        print(f"\n✓ Model downloaded to {MODEL_PATH}")
        return True
    except Exception as e:
        print(f"\n✗ Error downloading model: {e}")
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
    
    # YOLOv8 ONNX output format: [batch, 84, 8400] where 84 = 4 bbox + 80 classes
    output = outputs[0]  # Shape: [1, 84, 8400]
    
    # Reshape: [8400, 84]
    predictions = np.transpose(output, (0, 2, 1))[0]
    
    for pred in predictions:
        # Extract box coordinates and scores
        x_center, y_center, width, height = pred[:4]
        scores = pred[4:]
        
        # Find best class
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        
        if confidence > conf_threshold:
            class_name = COCO_CLASSES[class_id]
            detections.append((class_name, float(confidence)))
    
    return detections

# Camera devices
CAMERA1 = "/dev/video0"
CAMERA2 = "/dev/video2"

print("="*60)
print("YOLOv8 Object Detection (ONNX Runtime)")
print("="*60)
print()

# Download model
if not download_model():
    print("Failed to get model. Exiting.")
    sys.exit(1)

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
    print(f"  Output: {output_names[0]}")
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
    cap.set(cv2.CAP_PROP_FPS, 10)  # Lower FPS for ONNX processing
    
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
        
        time.sleep(0.1)  # ~10 FPS

except KeyboardInterrupt:
    print("\n\nStopping detection...")
finally:
    cap1.release()
    cap2.release()
    print("✓ Cameras released")
    print("Done!")

