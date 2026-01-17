#!/usr/bin/env python3
"""
Real-time Object Classification using TorchVision (pre-installed)
Classifies objects from both cameras and prints results to terminal
Uses MobileNet v2 which is already cached on the Jetson
"""

import cv2
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import numpy as np
import time
from datetime import datetime

# Load ImageNet class names
import urllib.request
import json

print("Loading MobileNet v2 model...")
try:
    # Load MobileNet v2 (already cached on Jetson)
    model = models.mobilenet_v2(pretrained=True)
    model.eval()  # Set to evaluation mode
    print("✓ MobileNet v2 model loaded!")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Download ImageNet class names
print("Loading ImageNet class names...")
try:
    url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
    urllib.request.urlretrieve(url, "/tmp/imagenet_classes.txt")
    with open("/tmp/imagenet_classes.txt", "r") as f:
        imagenet_classes = [line.strip() for line in f.readlines()]
    print(f"✓ Loaded {len(imagenet_classes)} ImageNet classes")
except Exception as e:
    print(f"Warning: Could not download class names: {e}")
    imagenet_classes = [f"class_{i}" for i in range(1000)]

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Camera devices
CAMERA1 = "/dev/video0"
CAMERA2 = "/dev/video2"

print("\n" + "="*60)
print("Starting object classification on cameras...")
print("Press Ctrl+C to stop")
print("="*60 + "\n")

# Open cameras
cap1 = cv2.VideoCapture(CAMERA1)
cap2 = cv2.VideoCapture(CAMERA2)

# Set camera properties
for cap, name in [(cap1, "Camera 1"), (cap2, "Camera 2")]:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)  # Lower FPS for classification
    
    if not cap.isOpened():
        print(f"⚠ Warning: {name} ({CAMERA1 if cap == cap1 else CAMERA2}) could not be opened")
    else:
        print(f"✓ {name} opened successfully")

print()

frame_count = 0
last_print_time = time.time()
print_interval = 3.0  # Print classifications every 3 seconds

def classify_frame(frame, model, transform, classes):
    """Classify a single frame and return top predictions"""
    try:
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        
        # Preprocess and add batch dimension
        input_tensor = transform(pil_image).unsqueeze(0)
        
        # Run inference
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
        # Get top 5 predictions
        top5_prob, top5_idx = torch.topk(probabilities, 5)
        
        results = []
        for i in range(5):
            idx = top5_idx[i].item()
            prob = top5_prob[i].item()
            class_name = classes[idx]
            results.append((class_name, prob))
        
        return results
    except Exception as e:
        return None

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
        
        classifications = {}
        
        # Process Camera 1
        if ret1:
            results1 = classify_frame(frame1, model, transform, imagenet_classes)
            if results1:
                # Filter for high confidence (>30%) and meaningful objects
                high_conf = [(name, conf) for name, conf in results1 if conf > 0.3]
                if high_conf:
                    classifications["Camera 1"] = high_conf
        
        # Process Camera 2
        if ret2:
            results2 = classify_frame(frame2, model, transform, imagenet_classes)
            if results2:
                # Filter for high confidence (>30%) and meaningful objects
                high_conf = [(name, conf) for name, conf in results2 if conf > 0.3]
                if high_conf:
                    classifications["Camera 2"] = high_conf
        
        # Print classifications every N seconds
        if current_time - last_print_time >= print_interval:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Frame {frame_count}")
            print("-" * 60)
            
            if classifications:
                for camera_name, objects in classifications.items():
                    print(f"\n{camera_name}:")
                    for obj_name, confidence in objects:
                        print(f"  • {obj_name} (confidence: {confidence:.1%})")
            else:
                print("No high-confidence objects detected")
            
            print("-" * 60)
            last_print_time = current_time
        
        # Small delay
        time.sleep(0.067)  # ~15 FPS

except KeyboardInterrupt:
    print("\n\nStopping object classification...")
finally:
    cap1.release()
    cap2.release()
    print("✓ Cameras released")
    print("Done!")

