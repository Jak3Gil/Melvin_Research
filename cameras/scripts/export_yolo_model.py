#!/usr/bin/env python3
"""Export YOLOv8 to ONNX format"""
from ultralytics import YOLO
import os

print("Loading YOLOv8n model...")
model = YOLO("yolov8n.pt")
print("Exporting to ONNX...")
model.export(format="onnx", imgsz=640, simplify=True)
print("✓ Export complete!")
print(f"Model saved to: yolov8n.onnx")
print(f"Size: {os.path.getsize('yolov8n.onnx') / 1024 / 1024:.1f} MB")

