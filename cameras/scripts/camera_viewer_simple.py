#!/usr/bin/env python3
"""
Simple Camera Viewer - Downloads frames continuously and displays them
Works with standard image viewers by updating image files
"""

import requests
import time
import sys
import os
from pathlib import Path

def download_frame(url, output_file, timeout=3):
    """Download a single frame from MJPEG stream"""
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        if response.status_code == 200:
            bytes_data = bytes()
            for chunk in response.iter_content(chunk_size=8192):
                bytes_data += chunk
                # Look for JPEG boundaries
                start = bytes_data.find(b'\xff\xd8')
                end = bytes_data.find(b'\xff\xd9')
                if start != -1 and end != -1:
                    jpg = bytes_data[start:end+2]
                    with open(output_file, 'wb') as f:
                        f.write(jpg)
                    return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    jetson_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.119"
    port = sys.argv[2] if len(sys.argv) > 2 else "8080"
    
    camera1_url = f"http://{jetson_ip}:{port}/stream1.mjpg"
    camera2_url = f"http://{jetson_ip}:{port}/stream2.mjpg"
    
    output_dir = Path("camera_images")
    output_dir.mkdir(exist_ok=True)
    
    cam1_file = output_dir / "camera1_live.jpg"
    cam2_file = output_dir / "camera2_live.jpg"
    
    print(f"Connecting to cameras...")
    print(f"Camera 1: {camera1_url}")
    print(f"Camera 2: {camera2_url}")
    print(f"Updating images in: {output_dir.absolute()}")
    print("Press Ctrl+C to stop")
    print()
    
    frame_count = 0
    last_update = time.time()
    
    try:
        while True:
            # Download frames
            success1 = download_frame(camera1_url, cam1_file)
            success2 = download_frame(camera2_url, cam2_file)
            
            if success1 and success2:
                frame_count += 1
                current_time = time.time()
                fps = 1.0 / (current_time - last_update) if frame_count > 1 else 0
                last_update = current_time
                print(f"\rFrames: {frame_count} | FPS: {fps:.1f} | Camera1: OK | Camera2: OK", end="", flush=True)
            else:
                print(f"\rFrame {frame_count}: Camera1: {'OK' if success1 else 'FAIL'}, Camera2: {'OK' if success2 else 'FAIL'}", end="", flush=True)
            
            # Small delay
            time.sleep(0.033)  # ~30 FPS
            
    except KeyboardInterrupt:
        print("\n\nStopping viewer...")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == '__main__':
    main()

