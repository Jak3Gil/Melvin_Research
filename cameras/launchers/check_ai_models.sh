#!/bin/bash
# Check for installed AI/ML models and libraries

echo "=========================================="
echo "AI/ML Installation Check"
echo "=========================================="
echo ""

echo "Python version:"
python3 --version
echo ""

echo "Installed ML/AI packages:"
pip3 list 2>/dev/null | grep -iE 'torch|tensorflow|opencv|cv2|yolo|detectron|mmdetection|onnx|onnxruntime|tensorrt|jetson|ultralytics|resnet|mobilenet|efficientnet' | head -30
echo ""

echo "Checking OpenCV:"
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')" 2>&1
echo ""

echo "Checking PyTorch:"
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')" 2>&1
echo ""

echo "Checking ONNX Runtime:"
python3 -c "import onnxruntime as ort; print(f'ONNX Runtime: {ort.__version__}'); print(f'Available providers: {ort.get_available_providers()}')" 2>&1
echo ""

echo "Checking TensorRT:"
python3 -c "import tensorrt; print(f'TensorRT: {tensorrt.__version__}')" 2>&1 || echo "TensorRT Python module not importable"
echo ""

echo "Checking NumPy, PIL:"
python3 -c "import numpy as np; from PIL import Image; print('NumPy and PIL/Pillow: Available')" 2>&1
echo ""

echo "Looking for model files:"
echo "ONNX models:"
find ~ -name '*.onnx' -type f 2>/dev/null | grep -v '.local/lib' | head -10
echo ""
echo "PyTorch models:"
find ~ -name '*.pt' -o -name '*.pth' 2>/dev/null | grep -v '.local/lib' | head -10
echo ""
echo "TensorRT engines:"
find ~ -name '*.trt' -o -name '*.engine' 2>/dev/null | head -10
echo ""

echo "CUDA packages:"
dpkg -l | grep -i cuda | head -10
echo ""

echo "Checking for jetson-inference:"
ls -la /usr/src/jetson-inference/ 2>/dev/null | head -5 || echo "jetson-inference not found in /usr/src/"
echo ""

echo "Checking for common model directories:"
for dir in ~/models ~/vision ~/ai ~/ml /usr/local/bin /opt/nvidia; do
    if [ -d "$dir" ]; then
        echo "Found: $dir"
        ls -la "$dir" 2>/dev/null | head -5
    fi
done

