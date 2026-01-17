#!/usr/bin/env python3
"""
View Jetson USB Cameras Remotely
Streams both USB cameras from Jetson to local computer via SSH
"""

import subprocess
import sys
import time
import os

# Jetson connection details
JETSON_HOST = "melvin@192.168.1.119"
JETSON_SSH = f"ssh {JETSON_HOST}"

# Camera devices on Jetson
CAMERA1 = "/dev/video0"
CAMERA2 = "/dev/video2"

def check_camera_access():
    """Check if cameras are accessible"""
    print("Checking camera access...")
    result = subprocess.run(
        f"{JETSON_SSH} 'ls -l {CAMERA1} {CAMERA2}'",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✓ Cameras found:")
        print(result.stdout)
        return True
    else:
        print("✗ Error accessing cameras:")
        print(result.stderr)
        return False

def get_camera_info(device):
    """Get camera information"""
    print(f"\nGetting info for {device}...")
    result = subprocess.run(
        f"{JETSON_SSH} 'v4l2-ctl --device={device} --list-formats-ext 2>/dev/null | head -20'",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Could not get info for {device}")

def capture_snapshot(device, output_file, width=640, height=480):
    """Capture a single snapshot from camera"""
    print(f"Capturing snapshot from {device}...")
    
    # Try using ffmpeg first
    cmd = (
        f"{JETSON_SSH} "
        f"'ffmpeg -f v4l2 -video_size {width}x{height} -i {device} "
        f"-frames:v 1 -y /tmp/{os.path.basename(output_file)} 2>&1'"
    )
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Copy file to local machine
        subprocess.run(f"scp {JETSON_HOST}:/tmp/{os.path.basename(output_file)} {output_file}", shell=True)
        print(f"✓ Snapshot saved to {output_file}")
        return True
    else:
        print(f"✗ Failed to capture from {device}")
        print(result.stderr)
        return False

def stream_mjpeg(device, port, width=640, height=480):
    """Stream MJPEG from camera via HTTP"""
    print(f"Starting MJPEG stream from {device} on port {port}...")
    
    cmd = (
        f"{JETSON_SSH} "
        f"'ffmpeg -f v4l2 -video_size {width}x{height} -framerate 30 -i {device} "
        f"-f mjpeg -qscale 5 - 2>/dev/null' | "
        f"ffmpeg -i pipe:0 -f mjpeg -listen 1 -timeout 60 http://0.0.0.0:{port}/"
    )
    
    print(f"Stream available at: http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    subprocess.run(cmd, shell=True)

def main():
    print("=" * 60)
    print("Jetson USB Camera Viewer")
    print("=" * 60)
    
    if not check_camera_access():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Camera Information")
    print("=" * 60)
    get_camera_info(CAMERA1)
    get_camera_info(CAMERA2)
    
    print("\n" + "=" * 60)
    print("Options:")
    print("=" * 60)
    print("1. Capture snapshots from both cameras")
    print("2. Stream camera 1 (MJPEG)")
    print("3. Stream camera 2 (MJPEG)")
    print("4. Stream both cameras (requires two terminals)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        print("\nCapturing snapshots...")
        capture_snapshot(CAMERA1, "camera1_snapshot.jpg")
        capture_snapshot(CAMERA2, "camera2_snapshot.jpg")
        print("\n✓ Snapshots captured! Check camera1_snapshot.jpg and camera2_snapshot.jpg")
    
    elif choice == "2":
        stream_mjpeg(CAMERA1, 8080)
    
    elif choice == "3":
        stream_mjpeg(CAMERA2, 8081)
    
    elif choice == "4":
        print("\nTo stream both cameras, run in two terminals:")
        print(f"Terminal 1: {sys.argv[0]} (choose option 2)")
        print(f"Terminal 2: {sys.argv[0]} (choose option 3)")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()

