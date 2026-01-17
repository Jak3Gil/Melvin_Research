#!/usr/bin/env python3
"""
Local Camera Viewer using OpenCV
Downloads and displays live video from Jetson cameras
"""

import cv2
import requests
import numpy as np
from threading import Thread
import sys

class CameraViewer:
    def __init__(self, camera1_url, camera2_url):
        self.camera1_url = camera1_url
        self.camera2_url = camera2_url
        self.running = True
        
    def get_frame(self, url):
        """Get single frame from MJPEG stream"""
        try:
            response = requests.get(url, stream=True, timeout=2)
            if response.status_code == 200:
                bytes_data = bytes()
                for chunk in response.iter_content(chunk_size=1024):
                    bytes_data += chunk
                    # Look for JPEG marker
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if img is not None:
                            return img
            return None
        except Exception as e:
            print(f"Error getting frame: {e}")
            return None
    
    def stream_camera(self, url, window_name):
        """Stream from a single camera"""
        while self.running:
            frame = self.get_frame(url)
            if frame is not None:
                cv2.imshow(window_name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    break
            else:
                print(f"Failed to get frame from {window_name}")
                import time
                time.sleep(0.1)
    
    def run(self):
        """Run dual camera viewer"""
        print("Starting camera viewer...")
        print("Press 'q' to quit")
        
        # Create windows
        cv2.namedWindow('Camera 1', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Camera 2', cv2.WINDOW_NORMAL)
        
        # Resize windows
        cv2.resizeWindow('Camera 1', 640, 480)
        cv2.resizeWindow('Camera 2', 640, 480)
        
        # Start streaming threads
        thread1 = Thread(target=self.stream_camera, args=(self.camera1_url, 'Camera 1'))
        thread2 = Thread(target=self.stream_camera, args=(self.camera2_url, 'Camera 2'))
        
        thread1.daemon = True
        thread2.daemon = True
        
        thread1.start()
        thread2.start()
        
        try:
            while self.running:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            cv2.destroyAllWindows()
            print("Viewer closed")

if __name__ == '__main__':
    jetson_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.119"
    port = sys.argv[2] if len(sys.argv) > 2 else "8080"
    
    camera1_url = f"http://{jetson_ip}:{port}/stream1.mjpg"
    camera2_url = f"http://{jetson_ip}:{port}/stream2.mjpg"
    
    print(f"Connecting to Camera 1: {camera1_url}")
    print(f"Connecting to Camera 2: {camera2_url}")
    
    viewer = CameraViewer(camera1_url, camera2_url)
    viewer.run()

