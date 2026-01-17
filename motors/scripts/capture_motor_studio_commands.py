#!/usr/bin/env python3
"""
Motor Studio Command Capture Script
Attempts to capture Motor Studio commands despite Windows port locking

Note: Windows typically locks COM ports, so this may not work directly.
Alternative: Use serial port monitor software (see instructions)
"""
import serial
import serial.tools.list_ports
import time
from datetime import datetime
import sys

def list_serial_ports():
    """List all available serial ports"""
    print("="*70)
    print("  AVAILABLE SERIAL PORTS")
    print("="*70)
    print()
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No serial ports found!")
        return []
    
    port_list = []
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Hardware ID: {port.hwid}")
        print()
        port_list.append(port.device)
    
    return port_list

def monitor_port_attempt(port_name, baud=921600):
    """
    Attempt to monitor port (may fail due to Windows port locking)
    
    Strategy: Try to open port in non-exclusive mode if possible
    """
    print("="*70)
    print("  MOTOR STUDIO COMMAND CAPTURE")
    print("="*70)
    print()
    print(f"Target port: {port_name}")
    print(f"Baud rate: {baud}")
    print()
    print("⚠️  WARNING: Windows locks COM ports!")
    print("If Motor Studio is already using this port, this will fail.")
    print()
    print("Instructions:")
    print("  1. Close Motor Studio first")
    print("  2. Run this script")
    print("  3. Note: You won't see Motor Studio commands this way")
    print("  4. Use serial port monitor software instead (see instructions)")
    print()
    
    input("Press Enter to attempt port opening...")
    print()
    
    try:
        # Try to open port
        ser = serial.Serial(
            port_name,
            baud,
            timeout=0.1,
            # Try to make it non-exclusive (doesn't always work on Windows)
            exclusive=False if hasattr(serial.Serial, 'exclusive') else None
        )
        
        print(f"✓ Port opened successfully!")
        print()
        print("Listening for commands...")
        print("(But Motor Studio can't connect if we're using the port)")
        print("Press Ctrl+C to stop")
        print()
        
        log_file = open('captured_commands.txt', 'w')
        packet_count = 0
        
        try:
            while True:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    packet_count += 1
                    
                    # Display
                    hex_str = data.hex(' ')
                    print(f"[{timestamp}] Packet #{packet_count}: {hex_str}")
                    
                    # Try ASCII
                    try:
                        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
                        if ascii_str.strip():
                            print(f"               ASCII: {ascii_str}")
                    except:
                        pass
                    
                    # Log
                    log_file.write(f"[{timestamp}] Packet #{packet_count}\n")
                    log_file.write(f"Hex: {hex_str}\n")
                    try:
                        log_file.write(f"ASCII: {ascii_str}\n")
                    except:
                        pass
                    log_file.write("\n")
                    log_file.flush()
                
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\nCapture stopped")
            log_file.close()
            print(f"Captured {packet_count} packets")
            print(f"Saved to: captured_commands.txt")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"✗ Failed to open port: {e}")
        print()
        print("This is expected if Motor Studio is using the port.")
        print()
        print("SOLUTION: Use serial port monitor software!")
        print("See: serial_port_monitor_instructions.md")
        return False

def create_manual_capture_instructions():
    """Print manual capture instructions"""
    print("\n" + "="*70)
    print("  MANUAL CAPTURE INSTRUCTIONS")
    print("="*70)
    print()
    print("Since Windows locks COM ports, use one of these methods:")
    print()
    print("METHOD 1: Serial Port Monitor Software (RECOMMENDED)")
    print("  1. Download Free Serial Port Monitor")
    print("     https://free-serial-port-monitor.com/")
    print("  2. Install and run it")
    print("  3. Start monitoring your COM port")
    print("  4. Run Motor Studio")
    print("  5. Export captured data")
    print()
    print("METHOD 2: Use Virtual Port Pair (com0com)")
    print("  1. Download com0com: https://sourceforge.net/projects/com0com/")
    print("  2. Install and create virtual port pair (COM10 <-> COM11)")
    print("  3. Connect Motor Studio to COM10")
    print("  4. Run this script on COM11")
    print()
    print("METHOD 3: Capture on Jetson (if possible)")
    print("  1. Connect USB-to-CAN to Jetson")
    print("  2. Use candump to capture CAN traffic")
    print("  3. Connect Motor Studio via USB on Windows")
    print("  4. Both see same CAN bus")
    print()
    print("See serial_port_monitor_instructions.md for detailed instructions")
    print()

def main():
    print("="*70)
    print("  MOTOR STUDIO COMMAND CAPTURE TOOL")
    print("="*70)
    print()
    
    # List ports
    ports = list_serial_ports()
    
    if not ports:
        print("No serial ports available!")
        return
    
    print("="*70)
    print()
    print("Note: This script will likely fail if Motor Studio is running")
    print("because Windows locks COM ports exclusively.")
    print()
    print("Options:")
    print("  1. Try to capture anyway (will fail if port in use)")
    print("  2. View manual capture instructions")
    print("  3. Exit")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        if len(ports) == 1:
            port_name = ports[0]
        else:
            port_num = input(f"Enter port number (1-{len(ports)}): ").strip()
            try:
                port_name = ports[int(port_num) - 1]
            except:
                print("Invalid choice")
                return
        
        monitor_port_attempt(port_name, 921600)
    
    elif choice == '2':
        create_manual_capture_instructions()
    
    else:
        print("Exiting")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
