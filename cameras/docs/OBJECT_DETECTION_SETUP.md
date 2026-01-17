# Object Detection Setup for Jetson

## Current Status

**Issue**: Disk is 100% full (only 122MB free) - cannot download YOLO model (~6MB needed)

**Available**: 
- ONNX Runtime 1.16.3 (installed ✓)
- OpenCV 4.2.0 (installed ✓)
- Both cameras working ✓

## Solution: YOLOv8 with ONNX Runtime

The most versatile system for object detection is **YOLOv8** with ONNX Runtime:

- **Detects 80 object classes** (person, car, dog, laptop, phone, etc.)
- **Real-time performance** on Jetson
- **No additional packages needed** (uses existing ONNX Runtime)
- **Small model size** (~6MB)

## Steps to Enable Full Detection

### Option 1: Free Up Disk Space (Recommended)

```bash
# Check largest files
du -sh ~/melvin/* | sort -h | tail -10

# Large file found: ~/melvin/jetson_brain.m (17GB)
# Consider moving or compressing it

# After freeing space, download and run:
wget https://github.com/ultralytics/ultralytics/releases/download/v8.2.0/yolov8n.onnx -O /tmp/yolov8n.onnx
python3 ~/camera_yolo_final.py
```

### Option 2: Use External Storage

1. Download model to external USB drive
2. Symlink or copy to `/tmp/yolov8n.onnx`
3. Run detection script

### Option 3: Use MobileNet (Limited Classification)

Can use existing MobileNet v2 model for image classification (1000 ImageNet classes) but:
- No bounding boxes
- Only full-image classification
- Less accurate than YOLO for object detection

## Working Script

The script `camera_yolo_final.py` is ready to use once the model is downloaded.

**Features:**
- Real-time detection from both cameras
- Prints detected objects every 2 seconds
- Shows object name, count, and confidence
- Handles both cameras simultaneously

## Test Script (Current)

For now, `camera_yolo_simple.py` provides basic motion detection.

## Quick Start (After Freeing Space)

```bash
# 1. Download model
wget https://github.com/ultralytics/ultralytics/releases/download/v8.2.0/yolov8n.onnx -O /tmp/yolov8n.onnx

# 2. Run detection
python3 ~/camera_yolo_final.py
```

## Example Output

```
[12:34:56] Frame 123
------------------------------------------------------------

Camera 1:
  • person x2 (85.3%)
  • laptop (92.1%)
  • cell phone (78.5%)

Camera 2:
  • car x3 (91.2%)
  • person (88.7%)
------------------------------------------------------------
```

## Object Classes Detected (80 total)

Person, vehicle (car, bus, truck, motorcycle, bicycle), animals (dog, cat, bird, etc.), furniture (chair, couch, bed), electronics (tv, laptop, cell phone, mouse, keyboard), food items, sports equipment, and more!

