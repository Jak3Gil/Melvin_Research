#!/usr/bin/env python3
"""Download YOLOv8 ONNX model using Python"""
import urllib.request
import os

urls = [
    "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.onnx",
    "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.onnx",
    "https://storage.googleapis.com/ultralytics/yolov8n.onnx",
]

output = "/tmp/yolov8n.onnx"

for url in urls:
    try:
        print(f"Trying: {url}")
        urllib.request.urlretrieve(url, output)
        size = os.path.getsize(output)
        if size > 1000000:
            print(f"✓ Downloaded! Size: {size/1024/1024:.1f} MB")
            exit(0)
        else:
            print(f"✗ File too small: {size} bytes")
            os.remove(output)
    except Exception as e:
        print(f"✗ Failed: {e}")
        continue

print("✗ All download attempts failed")
exit(1)
