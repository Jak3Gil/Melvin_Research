# Cameras – Vision, YOLO, Streaming

Camera capture, object detection (YOLO), streaming, and viewing scripts for USB cameras and Jetson.

## Structure

| Folder | Contents |
|--------|----------|
| **docs/** | OBJECT_DETECTION_SETUP, USB_CAMERAS_SETUP, VIDEO_STREAMING_SETUP, AI_MODELS_SUMMARY |
| **scripts/** | camera_*, stream_*, view_*, simple_camera/video, YOLO export/download |
| **launchers/** | capture, start/stop streams, view_cameras*.ps1, check_ai_models, install_yolo |
| **models/** | yolov8n.onnx, yolov8n.pt (YOLO weights) |

## Paths

- **camera_images** (captured/streamed images) stays at **project root**.
- Launchers that use `camera_images` switch to the project root before running.
- YOLO models: `cameras/models/`. For scripts that expect `yolov8n.pt` in CWD, run from `cameras/models/` or set the path in the script.

## Quick start

- **View cameras (Jetson):** `launchers/view_cameras.ps1`
- **Live / ultra-fast:** `launchers/view_cameras_live.ps1`, `launchers/view_cameras_ultra_fast.ps1`
- **Stream and view:** `launchers/stream_and_view.ps1`
- **HTML viewer:** `view_jetson_cameras.html` (open in browser)

