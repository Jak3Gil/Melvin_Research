#!/usr/bin/env python3
"""
Automated Command Capture on Jetson
Captures commands sent to USB-to-CAN adapter on Jetson
Works when Motor Studio connects remotely or when USB-to-CAN is accessed
"""
import serial
import time
from datetime import datetime
import sys

PORT = '/dev/ttyUSB0'  # Default, will check for ttyUSB1 if needed
BAUD = 921600

def find_usb_port():
    """Find USB-to-CAN adapter port"""
    import os
    
    ports_to_try = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']
    
    for port in ports_to_try:
        if os.path.exists(port):
            return port
    
    return None

def capture_commands(port, output_file, duration=300):
    """
    Capture commands automatically
    
    Args:
        port: Serial port path
        output_file: Output file for captured data
        duration: Capture duration in seconds (default 5 minutes)
    """
    print("="*70)
    print("  AUTOMATED COMMAND CAPTURE - JETSON")
    print("="*70)
    print()
    print(f"Port: {port}")
    print(f"Baud: {BAUD}")
    print(f"Output: {output_file}")
    print(f"Duration: {duration} seconds (or Ctrl+C to stop)")
    print()
    print("Capturing commands...")
    print("(Motor Studio or other software will send commands)")
    print()
    
    try:
        ser = serial.Serial(port, BAUD, timeout=0.1)
        print(f"Port opened successfully!")
        print()
        
        packet_count = 0
        start_time = time.time()
        
        with open(output_file, 'w') as f:
            # Write header
            f.write(f"MOTOR STUDIO COMMAND CAPTURE\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Port: {port}\n")
            f.write(f"Baud: {BAUD}\n")
            f.write("="*70 + "\n\n")
            
            try:
                while time.time() - start_time < duration:
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting)
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        packet_count += 1
                        
                        # Format output
                        hex_str = data.hex(' ')
                        
                        # Display
                        print(f"[{timestamp}] Packet #{packet_count}: {hex_str}")
                        
                        # Save
                        f.write(f"[{timestamp}] Packet #{packet_count}\n")
                        f.write(f"Hex: {hex_str}\n")
                        
                        # Try ASCII
                        try:
                            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
                            if any(c != '.' for c in ascii_str):
                                f.write(f"ASCII: {ascii_str}\n")
                        except:
                            pass
                        
                        f.write("\n")
                        f.flush()
                    
                    time.sleep(0.01)
                
                print(f"\n\nCapture complete after {duration} seconds")
                print(f"Captured {packet_count} packets")
                
            except KeyboardInterrupt:
                elapsed = time.time() - start_time
                print(f"\n\nCapture stopped by user")
                print(f"Captured {packet_count} packets in {elapsed:.1f} seconds")
        
        ser.close()
        return packet_count
        
    except serial.SerialException as e:
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print(f"  1. Check if {port} exists: ls -la {port}")
        print(f"  2. Check permissions: sudo chmod 666 {port}")
        print(f"  3. Check if port is in use: lsof {port}")
        return 0

def main():
    print("="*70)
    print("  AUTOMATED COMMAND CAPTURE - JETSON")
    print("="*70)
    print()
    
    # Find USB port
    port = find_usb_port()
    
    if not port:
        print("No USB-to-CAN adapter found!")
        print()
        print("Looking for: /dev/ttyUSB0, /dev/ttyUSB1, /dev/ttyUSB2")
        print()
        print("Make sure:")
        print("  1. USB-to-CAN adapter is connected to Jetson")
        print("  2. Device is powered on")
        print("  3. Check with: ls -la /dev/ttyUSB*")
        return
    
    print(f"Found USB-to-CAN adapter: {port}")
    print()
    
    # Set permissions
    import subprocess
    try:
        subprocess.run(['sudo', 'chmod', '666', port], capture_output=True, check=False)
        print(f"Set permissions on {port}")
    except:
        pass
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'motor_studio_capture_{timestamp}.txt'
    
    # Capture duration (5 minutes default, or until Ctrl+C)
    duration = 300  # 5 minutes
    
    print("Starting automated capture...")
    print()
    print("Instructions:")
    print("  1. Keep this script running")
    print("  2. Connect Motor Studio on Windows PC")
    print("  3. If USB-to-CAN is on Jetson, Motor Studio needs to connect remotely")
    print("  4. OR move USB-to-CAN to Windows PC to use with Motor Studio directly")
    print("  5. Perform actions in Motor Studio")
    print("  6. Commands will be captured here")
    print()
    
    packet_count = capture_commands(port, output_file, duration)
    
    if packet_count > 0:
        print()
        print("="*70)
        print("  CAPTURE COMPLETE")
        print("="*70)
        print()
        print(f"Captured {packet_count} packets")
        print(f"Saved to: {output_file}")
        print()
        print("Next step: Analyze captured commands")
        print(f"  python analyze_captured_commands.py {output_file}")
        print()
    else:
        print()
        print("No packets captured.")
        print()
        print("Possible reasons:")
        print("  1. Motor Studio not sending commands")
        print("  2. USB-to-CAN adapter not properly connected")
        print("  3. Wrong port (try /dev/ttyUSB1 instead)")
        print("  4. Need to connect Motor Studio to this USB-to-CAN adapter")
        print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

