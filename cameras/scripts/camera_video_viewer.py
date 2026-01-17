#!/usr/bin/env python3
"""
Live Video Viewer for Camera Streams
Uses OpenCV to display UDP video streams
"""

import cv2
import socket
import numpy as np
import sys

class UDPVideoReceiver:
    def __init__(self, port, window_name):
        self.port = port
        self.window_name = window_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.sock.settimeout(1.0)
        
    def receive_frame(self):
        """Receive a video frame from UDP stream"""
        try:
            data, addr = self.sock.recvfrom(65536)
            # Decode MPEG-TS stream (simplified - may need better parsing)
            return data
        except socket.timeout:
            return None
    
    def close(self):
        self.sock.close()

def view_stream(port, window_name):
    """View video stream from UDP port"""
    receiver = UDPVideoReceiver(port, window_name)
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    
    print(f"Receiving stream on port {port}...")
    print("Press 'q' to quit")
    
    try:
        while True:
            data = receiver.receive_frame()
            if data:
                # For MPEG-TS, we'd need to parse it properly
                # For now, try to decode as JPEG if it looks like one
                if data[:2] == b'\xff\xd8':  # JPEG header
                    nparr = np.frombuffer(data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if img is not None:
                        cv2.imshow(window_name, img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        receiver.close()
        cv2.destroyAllWindows()

def main():
    print("Video Stream Viewer")
    print("===================")
    print("Camera 1: UDP port 5004")
    print("Camera 2: UDP port 5005")
    print("")
    
    # Try to view both streams
    try:
        import threading
        
        thread1 = threading.Thread(target=view_stream, args=(5004, 'Camera 1'))
        thread2 = threading.Thread(target=view_stream, args=(5005, 'Camera 2'))
        
        thread1.daemon = True
        thread2.daemon = True
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
    except Exception as e:
        print(f"Error: {e}")
        print("Note: UDP video streams require proper MPEG-TS parsing")
        print("Consider using VLC instead for better compatibility")

if __name__ == '__main__':
    main()

