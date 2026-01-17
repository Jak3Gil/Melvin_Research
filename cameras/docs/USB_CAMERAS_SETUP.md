# USB Cameras Setup on Jetson

## Camera Detection Summary

Both USB cameras are successfully detected and working on the Jetson:

### Camera 1
- **Device**: `/dev/video0` (primary), `/dev/video1` (metadata)
- **Type**: HDMI USB Camera (UVC)
- **USB Bus**: `usb-3610000.xhci-4.3`
- **Serial**: `78b8181c9d01ae53`
- **Driver**: uvcvideo (Linux UVC driver)

### Camera 2
- **Device**: `/dev/video2` (primary), `/dev/video3` (metadata)
- **Type**: HDMI USB Camera (UVC)
- **USB Bus**: `usb-3610000.xhci-4.4`
- **Serial**: `2030201e5148c4e3`
- **Driver**: uvcvideo (Linux UVC driver)

## Quick Capture Commands

### Single Capture (Both Cameras)

```bash
# On Jetson
~/capture_cameras.sh
```

This captures images from both cameras and saves them to:
- `~/camera_captures/camera1.jpg`
- `~/camera_captures/camera2.jpg`

### View Images Remotely

From your Windows computer:

```powershell
# One-time capture and view
.\view_cameras.ps1

# Live continuous view (updates every 2 seconds)
.\view_cameras_live.ps1

# Custom interval (e.g., 5 seconds)
.\view_cameras_live.ps1 -Interval 5
```

## Manual Capture Commands

### Using fswebcam (installed on Jetson)

```bash
# Camera 1 - High resolution
fswebcam -d /dev/video0 -r 1280x720 --no-banner ~/camera1.jpg

# Camera 2 - High resolution
fswebcam -d /dev/video2 -r 1280x720 --no-banner ~/camera2.jpg

# Lower resolution (if high res fails)
fswebcam -d /dev/video0 -r 640x480 --no-banner ~/camera1.jpg
fswebcam -d /dev/video2 -r 640x480 --no-banner ~/camera2.jpg
```

### Check Camera Capabilities

```bash
# List all video devices
v4l2-ctl --list-devices

# Get detailed info for Camera 1
v4l2-ctl --device=/dev/video0 --all

# Get detailed info for Camera 2
v4l2-ctl --device=/dev/video2 --all

# List supported formats
v4l2-ctl --device=/dev/video0 --list-formats-ext
v4l2-ctl --device=/dev/video2 --list-formats-ext
```

## File Locations

### On Jetson
```
/home/melvin/
├── camera_captures/
│   ├── camera1.jpg          # Latest Camera 1 image
│   ├── camera2.jpg          # Latest Camera 2 image
│   └── camera*_YYYYMMDD_HHMMSS.jpg  # Timestamped captures
├── capture_cameras.sh       # Single capture script
└── stream_cameras.sh        # Continuous capture script
```

### On Windows Computer
```
F:\Melvin_Research\Melvin_Research\
├── camera_images/
│   ├── camera1.jpg          # Transferred Camera 1 image
│   └── camera2.jpg          # Transferred Camera 2 image
├── view_cameras.ps1         # One-time viewer script
└── view_cameras_live.ps1    # Live viewer script
```

## Continuous Streaming

### On Jetson (Background Process)

```bash
# Capture every 2 seconds (infinite)
~/stream_cameras.sh 2 0

# Capture every 1 second, 10 times total
~/stream_cameras.sh 1 10
```

### From Windows (Live View)

```powershell
# Continuous view, updates every 2 seconds
.\view_cameras_live.ps1

# Updates every 1 second
.\view_cameras_live.ps1 -Interval 1

# Limited to 20 refreshes
.\view_cameras_live.ps1 -Interval 2 -MaxRefreshes 20
```

## Troubleshooting

### Cameras Not Detected

```bash
# Check USB devices
lsusb | grep -i camera

# Check video devices
ls -la /dev/video*

# Check if cameras are being used
lsof /dev/video0
lsof /dev/video2
```

### Permission Issues

```bash
# Add user to video group (if needed)
sudo usermod -aG video $USER
# Log out and back in for changes to take effect
```

### Image Capture Fails

```bash
# Try different resolutions
fswebcam -d /dev/video0 -r 640x480 --no-banner test.jpg

# Check camera is not locked
sudo fuser -v /dev/video0
sudo fuser -k /dev/video0  # Kill processes using camera
```

### Poor Image Quality

```bash
# List available resolutions
v4l2-ctl --device=/dev/video0 --list-formats-ext

# Set specific format
v4l2-ctl --device=/dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat=MJPG
```

## Camera Specifications

Both cameras support:
- **Video Capture**: Yes
- **Metadata Capture**: Yes
- **Streaming**: Yes
- **Extended Pixel Formats**: Yes

Supported resolutions (typically):
- 640x480 (VGA)
- 1280x720 (HD/720p)
- 1920x1080 (Full HD/1080p) - may require MJPEG format

## Integration with Melvin

You can integrate camera capture into the Melvin system:

### C Example

```c
#include <stdlib.h>
#include <stdio.h>

void capture_camera1() {
    system("fswebcam -d /dev/video0 -r 1280x720 --no-banner /tmp/melvin_cam1.jpg");
}

void capture_camera2() {
    system("fswebcam -d /dev/video2 -r 1280x720 --no-banner /tmp/melvin_cam2.jpg");
}

// EXECUTABLE node example
void melvin_camera_node(MelvinFile *g, uint64_t node_id) {
    capture_camera1();
    capture_camera2();
    // Process images or trigger events based on image content
}
```

### Python Example

```python
import subprocess
import os

def capture_camera(device, output_file):
    """Capture image from specified camera device."""
    cmd = [
        'fswebcam',
        '-d', device,
        '-r', '1280x720',
        '--no-banner',
        output_file
    ]
    subprocess.run(cmd, capture_output=True)

# Capture both cameras
capture_camera('/dev/video0', '/tmp/camera1.jpg')
capture_camera('/dev/video2', '/tmp/camera2.jpg')
```

## Notes

- Both cameras are identical models (HDMI USB Camera)
- They use the standard Linux UVC (USB Video Class) driver
- Images are captured in JPEG format
- Default capture location: `~/camera_captures/`
- Images can be transferred to Windows via SCP for viewing
- Live viewing requires periodic re-capture and transfer

---

**Last Updated**: January 2026  
**Tested On**: NVIDIA Jetson AGX Orin  
**Cameras**: 2x HDMI USB Camera (UVC)

