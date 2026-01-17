#!/usr/bin/env python3
"""
Monitor serial port traffic to capture Motor Studio's commands
Run this while Motor Studio is detecting devices
"""
import serial
import time
import sys
from datetime import datetime

def monitor_traffic(port, baudrate=921600, duration=30):
    """Monitor serial port and capture all traffic"""
    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
        print(f"[OK] Monitoring {port} at {baudrate} baud")
        print(f"Monitoring for {duration} seconds...")
        print("Please run Motor Studio's detection now!\n")
        print("="*60)
        
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < duration:
            # Read any incoming data
            data = ser.read(1000)
            if data and len(data) > 0:
                packet_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"[{timestamp}] Packet #{packet_count} ({len(data)} bytes):")
                print(f"  Hex: {data.hex()}")
                
                # Try to decode as ASCII
                try:
                    ascii_str = data.decode('ascii', errors='ignore')
                    if ascii_str.strip():
                        print(f"  ASCII: {ascii_str[:80]}")
                except:
                    pass
                
                print()
            
            time.sleep(0.01)
        
        ser.close()
        print("="*60)
        print(f"[OK] Monitoring complete! Captured {packet_count} packet(s)")
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        print("\nMake sure Motor Studio is closed first!")
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        ser.close()
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    duration = 30
    if len(sys.argv) > 2:
        duration = int(sys.argv[2])
    
    print("="*60)
    print("Motor Studio Traffic Monitor")
    print("="*60)
    print(f"Port: {port}")
    print(f"Duration: {duration} seconds")
    print("\nINSTRUCTIONS:")
    print("1. Close Motor Studio")
    print("2. Run this script")
    print("3. Open Motor Studio and enable multi-device + detect")
    print("4. Watch the commands appear here!")
    print("="*60)
    print()
    
    monitor_traffic(port, duration=duration)

