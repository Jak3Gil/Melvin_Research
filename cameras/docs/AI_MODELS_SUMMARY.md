# AI/ML Models and Vision Libraries on Jetson

## Installed Libraries

### Deep Learning Frameworks
- **PyTorch**: 2.4.1 (CUDA not available - may need configuration)
- **TensorRT**: 8.5.2.2 (NVIDIA's inference optimizer)
- **ONNX Runtime**: 1.16.3 (CPU execution provider available)
- **TorchVision**: 0.19.1 (Image classification and detection models)

### Computer Vision
- **OpenCV**: 4.2.0 (Image/video processing)
- **NumPy**: Available
- **PIL/Pillow**: Available

### CUDA Infrastructure
- **CUDA 11.4**: Installed with various packages
- Note: PyTorch CUDA not currently available (may need CUDA-enabled PyTorch build)

## Available Models

### Pre-trained PyTorch Models (cached)
- **Whisper tiny.pt**: Speech recognition model (~/.cache/whisper/tiny.pt)
- **MobileNet v2**: Image classification model (~/.cache/torch/hub/checkpoints/mobilenet_v2-*.pth)

### ONNX Models
- **Piper TTS models**: Text-to-speech (en_US-amy-medium.onnx, en_US-lessac-medium.onnx)
- Example ONNX models in onnxruntime datasets

### Not Installed
- **YOLO/Ultralytics**: Not found
- **jetson-inference**: Not found
- **TensorFlow**: Not installed
- **Object detection models**: None specifically for vision classification

## Capabilities for Live Video Classification

### What You CAN Do (with current setup):
1. **Use TorchVision pre-trained models** for image classification:
   - ResNet, MobileNet, EfficientNet, etc.
   - Can classify images into 1000 ImageNet categories
   
2. **Use OpenCV** for:
   - Video capture and processing
   - Image preprocessing
   - Basic computer vision operations

3. **Use ONNX Runtime** for:
   - Running ONNX models (if you download object detection models)
   - Efficient inference on CPU

### What You CANNOT Do (without installation):
1. **Object detection** (YOLO, Detectron, etc.) - not installed
2. **Custom vision models** - none present
3. **GPU-accelerated PyTorch** - CUDA not available for PyTorch

## Recommendations for Video Classification

### Option 1: Use TorchVision Pre-trained Models
- Use ResNet, MobileNet, or EfficientNet for image classification
- Process frames from camera streams
- Classify objects/scenes in real-time

### Option 2: Install YOLO (Ultralytics)
- Install: `pip install ultralytics`
- Download YOLOv8 or YOLOv5 models
- Detect and classify objects in video streams

### Option 3: Download ONNX Object Detection Models
- Download YOLO ONNX models from ONNX Model Zoo
- Use ONNX Runtime for inference
- Good performance on Jetson

### Option 4: Use jetson-inference (NVIDIA's Toolkit)
- Install jetson-inference SDK
- Pre-optimized models for Jetson
- Best performance on Jetson hardware

## Next Steps

Would you like to:
1. Set up a simple image classifier using TorchVision?
2. Install YOLO for object detection?
3. Create a video classification pipeline that processes frames from your cameras?
4. Set up jetson-inference for optimized performance?

