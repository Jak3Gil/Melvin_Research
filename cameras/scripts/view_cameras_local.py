#!/usr/bin/env python3
"""
View Jetson USB Cameras Locally
Streams both cameras from Jetson and displays them on local machine
"""

import subprocess
import sys
import time
import os
import threading
from pathlib import Path

# Jetson connection details
JETSON_HOST = "melvin@192.168.1.119"
JETSON_SSH = f"ssh {JETSON_HOST}"

# Camera devices
CAMERA1 = "/dev/video0"
CAMERA2 = "/dev/video2"

# Stream ports
PORT1 = 8080
PORT2 = 8081

def check_ffmpeg_local():
    """Check if ffmpeg is available locally"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def capture_snapshot(device, output_file, width=640, height=480):
    """Capture a snapshot from camera"""
    print(f"Capturing from {device}...")
    
    cmd = (
        f"{JETSON_SSH} "
        f"'timeout 3 ffmpeg -f v4l2 -video_size {width}x{height} -i {device} "
        f"-frames:v 1 -y /tmp/snapshot.jpg 2>/dev/null'"
    )
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        subprocess.run(f"scp {JETSON_HOST}:/tmp/snapshot.jpg {output_file}", shell=True)
        print(f"✓ Saved to {output_file}")
        return True
    return False

def stream_camera_ssh(device, port, width=640, height=480):
    """Stream camera through SSH pipe"""
    print(f"Starting stream from {device} on port {port}...")
    
    # Command to run on Jetson
    jetson_cmd = (
        f"ffmpeg -f v4l2 -video_size {width}x{height} -framerate 30 "
        f"-i {device} -f mjpeg -qscale 2 - 2>/dev/null"
    )
    
    # Local command to receive and serve
    if check_ffmpeg_local():
        local_cmd = f"ffmpeg -i pipe:0 -f mjpeg -listen 1 -timeout 60 http://0.0.0.0:{port}/"
        cmd = f"{JETSON_SSH} '{jetson_cmd}' | {local_cmd}"
    else:
        # Fallback: save frames locally
        print("ffmpeg not found locally, saving frames instead...")
        return stream_camera_frames(device, port, width, height)
    
    print(f"Stream available at: http://localhost:{port}")
    subprocess.run(cmd, shell=True)

def stream_camera_frames(device, port, width=640, height=480):
    """Stream by continuously capturing frames"""
    print(f"Capturing frames from {device}...")
    frame_dir = Path("camera_frames")
    frame_dir.mkdir(exist_ok=True)
    
    frame_count = 0
    while True:
        output = frame_dir / f"cam{port}_{frame_count:05d}.jpg"
        if capture_snapshot(device, str(output), width, height):
            frame_count += 1
            time.sleep(0.1)  # ~10 FPS

def start_jetson_streams():
    """Start streaming servers on Jetson"""
    print("Starting streaming servers on Jetson...")
    
    script = f"""
#!/bin/bash
WIDTH=640
HEIGHT=480
FPS=30

# Stream Camera 1
ffmpeg -f v4l2 -video_size ${{WIDTH}}x${{HEIGHT}} -framerate $FPS -i {CAMERA1} \\
    -f mjpeg -qscale 2 -listen 1 -timeout 60 http://0.0.0.0:{PORT1}/ > /tmp/cam1.log 2>&1 &
echo $!

# Stream Camera 2  
ffmpeg -f v4l2 -video_size ${{WIDTH}}x${{HEIGHT}} -framerate $FPS -i {CAMERA2} \\
    -f mjpeg -qscale 2 -listen 1 -timeout 60 http://0.0.0.0:{PORT2}/ > /tmp/cam2.log 2>&1 &
echo $!
"""
    
    # Upload and run script
    with open("/tmp/start_streams.sh", "w") as f:
        f.write(script)
    
    subprocess.run(f"scp /tmp/start_streams.sh {JETSON_HOST}:/tmp/", shell=True)
    result = subprocess.run(
        f"{JETSON_SSH} 'chmod +x /tmp/start_streams.sh && /tmp/start_streams.sh'",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        pids = result.stdout.strip().split('\n')
        print(f"✓ Streams started (PIDs: {pids[0]}, {pids[1]})")
        print(f"  Camera 1: http://192.168.1.119:{PORT1}")
        print(f"  Camera 2: http://192.168.1.119:{PORT2}")
        return pids
    else:
        print("✗ Failed to start streams")
        print(result.stderr)
        return None

def stop_jetson_streams():
    """Stop streaming servers on Jetson"""
    print("Stopping streams...")
    subprocess.run(
        f"{JETSON_SSH} 'pkill -f \"ffmpeg.*video[02]\"'",
        shell=True
    )
    print("✓ Streams stopped")

def open_html_viewer():
    """Open HTML viewer in default browser"""
    html_file = Path("view_jetson_cameras.html")
    if html_file.exists():
        import webbrowser
        webbrowser.open(f"file://{html_file.absolute()}")
        print(f"✓ Opened viewer: {html_file}")
    else:
        print("✗ HTML viewer not found")

def main():
    print("=" * 60)
    print("Jetson USB Camera Viewer")
    print("=" * 60)
    print(f"\nCameras:")
    print(f"  Camera 1: {CAMERA1}")
    print(f"  Camera 2: {CAMERA2}")
    print()
    
    print("Options:")
    print("1. Start streaming servers on Jetson (view in browser)")
    print("2. Capture snapshots from both cameras")
    print("3. Stream through SSH pipe (requires local ffmpeg)")
    print("4. Open HTML viewer")
    print("5. Stop streaming servers")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        pids = start_jetson_streams()
        if pids:
            print("\n✓ Streams are running!")
            print("  Open view_jetson_cameras.html in your browser")
            print("  Or visit directly:")
            print(f"    Camera 1: http://192.168.1.119:{PORT1}")
            print(f"    Camera 2: http://192.168.1.119:{PORT2}")
            input("\nPress Enter to stop streams...")
            stop_jetson_streams()
    
    elif choice == "2":
        print("\nCapturing snapshots...")
        capture_snapshot(CAMERA1, "camera1_snapshot.jpg")
        capture_snapshot(CAMERA2, "camera2_snapshot.jpg")
        print("\n✓ Snapshots saved!")
    
    elif choice == "3":
        print("\nStarting streams through SSH...")
        print("Press Ctrl+C to stop")
        try:
            t1 = threading.Thread(target=stream_camera_ssh, args=(CAMERA1, PORT1))
            t2 = threading.Thread(target=stream_camera_ssh, args=(CAMERA2, PORT2))
            t1.daemon = True
            t2.daemon = True
            t1.start()
            time.sleep(1)
            t2.start()
            t1.join()
            t2.join()
        except KeyboardInterrupt:
            print("\nStopping streams...")
    
    elif choice == "4":
        open_html_viewer()
    
    elif choice == "5":
        stop_jetson_streams()
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()

