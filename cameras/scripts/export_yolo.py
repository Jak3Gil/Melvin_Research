#!/usr/bin/env python3
import os
from ultralytics import YOLO

print("Loading YOLOv8n...")
model = YOLO('yolov8n')  # This downloads the PyTorch model
print("Exporting to ONNX...")
model.export(format='onnx', imgsz=640)
print("✓ Export complete")

# Find and copy to /tmp
import glob
model_paths = glob.glob(os.path.expanduser('~/.ultralytics/models/**/yolov8n.onnx'), recursive=True)
if model_paths:
    import shutil
    src = model_paths[0]
    dst = '/tmp/yolov8n.onnx'
    shutil.copy(src, dst)
    size = os.path.getsize(dst) / 1024 / 1024
    print(f"✓ Copied {src} to {dst} ({size:.1f}MB)")
else:
    print("✗ Could not find exported model")

