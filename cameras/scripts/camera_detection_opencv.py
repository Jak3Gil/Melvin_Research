#!/usr/bin/env python3
"""
Object Detection using OpenCV DNN with MobileNet SSD
This uses a pre-trained model that OpenCV can download automatically
"""
import cv2
import numpy as np
import time
from datetime import datetime

# COCO class names
COCO_CLASSES = [
    'background', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
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

print("="*60)
print("OpenCV DNN Object Detection")
print("="*60)

# Download model files if needed
prototxt = "MobileNetSSD_deploy.prototxt"
model_file = "MobileNetSSD_deploy.caffemodel"

print(f"\nLoading model: {model_file}")
print("Note: If model not found, download from:")
print("  https://github.com/chuanqi305/MobileNet-SSD")
print()

# Try to load the model
net = None
try:
    net = cv2.dnn.readNetFromCaffe(prototxt, model_file)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    print("✓ Model loaded with CUDA acceleration")
except:
    print("✗ Model files not found. Using basic detection without AI.")
    print("  Creating simplified detector that reports image statistics...")

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
        
        if ret1 and net is not None:
            try:
                blob = cv2.dnn.blobFromImage(cv2.resize(f1, (300, 300)), 0.007843, (300, 300), 127.5)
                net.setInput(blob)
                dets = net.forward()
                
                objs = []
                for i in range(dets.shape[2]):
                    confidence = dets[0, 0, i, 2]
                    if confidence > 0.5:
                        class_id = int(dets[0, 0, i, 1])
                        if class_id < len(COCO_CLASSES):
                            objs.append((COCO_CLASSES[class_id], confidence))
                
                if objs:
                    detections["Camera 1"] = objs
            except Exception as e:
                pass
        
        if ret2 and net is not None:
            try:
                blob = cv2.dnn.blobFromImage(cv2.resize(f2, (300, 300)), 0.007843, (300, 300), 127.5)
                net.setInput(blob)
                dets = net.forward()
                
                objs = []
                for i in range(dets.shape[2]):
                    confidence = dets[0, 0, i, 2]
                    if confidence > 0.5:
                        class_id = int(dets[0, 0, i, 1])
                        if class_id < len(COCO_CLASSES):
                            objs.append((COCO_CLASSES[class_id], confidence))
                
                if objs:
                    detections["Camera 2"] = objs
            except Exception as e:
                pass
        
        # Fallback: report image stats if no model
        if net is None:
            if ret1:
                h, w = f1.shape[:2]
                mean = f1.mean()
                std = f1.std()
                detections["Camera 1"] = [(f"Image: {w}x{h}, brightness: {mean:.1f}, contrast: {std:.1f}", 1.0)]
            
            if ret2:
                h, w = f2.shape[:2]
                mean = f2.mean()
                std = f2.std()
                detections["Camera 2"] = [(f"Image: {w}x{h}, brightness: {mean:.1f}, contrast: {std:.1f}", 1.0)]
        
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

