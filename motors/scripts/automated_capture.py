#!/usr/bin/env python3
"""
Automated Motor Studio Command Capture
Attempts to automate command capture despite Windows limitations
"""
import serial
import serial.tools.list_ports
import time
import subprocess
import os
import sys
from datetime import datetime
import json

def find_com_ports():
    """Find all COM ports"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def check_port_available(port_name):
    """Check if port is available (not locked)"""
    try:
        ser = serial.Serial(port_name, 921600, timeout=0.1)
        ser.close()
        return True
    except serial.SerialException:
        return False

def wait_for_port_connection(port_name, timeout=60):
    """Wait for port to become available (Motor Studio connects)"""
    print(f"Waiting for {port_name} to become available...")
    print("(Start Motor Studio now and connect to this port)")
    print()
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_port_available(port_name):
            print(f"Port {port_name} is available!")
            time.sleep(2)  # Give Motor Studio time to initialize
            return True
        time.sleep(0.5)
        print(".", end="", flush=True)
    
    print("\n✗ Timeout waiting for port")
    return False

def capture_with_motor_studio_instructions(port_name):
    """Provide instructions for manual capture"""
    print("="*70)
    print("  AUTOMATED CAPTURE - INSTRUCTIONS")
    print("="*70)
    print()
    print("Due to Windows COM port locking, full automation isn't possible.")
    print()
    print("OPTION 1: Use Serial Port Monitor Software (RECOMMENDED)")
    print("-"*70)
    print("1. Download Free Serial Port Monitor:")
    print("   https://free-serial-port-monitor.com/")
    print()
    print("2. Install and run it")
    print()
    print("3. Start monitoring:", port_name)
    print()
    print("4. Open Motor Studio in another window")
    print()
    print("5. Connect Motor Studio to:", port_name)
    print()
    print("6. Perform actions in Motor Studio (scan, enable, move motors)")
    print()
    print("7. Export captured data as CSV")
    print()
    print("8. Run: python analyze_captured_commands.py <captured_file.csv>")
    print()
    
    print("OPTION 2: Use com0com Virtual Ports")
    print("-"*70)
    print("1. Download com0com: https://sourceforge.net/projects/com0com/")
    print("2. Install and create virtual port pair (COM10 <-> COM11)")
    print("3. Connect Motor Studio to COM10")
    print("4. Run capture script on COM11")
    print()
    
    print("OPTION 3: Check if port becomes available")
    print("-"*70)
    print("This script will attempt to open the port when Motor Studio closes it.")
    print("(Motor Studio must close the port for us to capture)")
    print()
    
    choice = input("Try to wait for port availability? (y/n): ").strip().lower()
    if choice == 'y':
        return wait_for_port_and_capture(port_name)
    
    return False

def wait_for_port_and_capture(port_name):
    """Wait for port and try to capture"""
    if wait_for_port_connection(port_name):
        print("\nPort is available - attempting capture...")
        print("(Note: Motor Studio must close the port for this to work)")
        print()
        
        try:
            ser = serial.Serial(port_name, 921600, timeout=0.1)
            print("✓ Port opened!")
            print("Capturing commands... (Press Ctrl+C to stop)")
            print()
            
            capture_file = f'motor_studio_capture_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            with open(capture_file, 'w') as f:
                packet_count = 0
                try:
                    while True:
                        if ser.in_waiting > 0:
                            data = ser.read(ser.in_waiting)
                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            packet_count += 1
                            
                            hex_str = data.hex(' ')
                            line = f"[{timestamp}] Packet #{packet_count}: {hex_str}\n"
                            print(line.strip())
                            f.write(line)
                            f.flush()
                        
                        time.sleep(0.01)
                except KeyboardInterrupt:
                    print(f"\n\nCaptured {packet_count} packets")
                    print(f"Saved to: {capture_file}")
            
            ser.close()
            return True
            
        except serial.SerialException as e:
            print(f"✗ Cannot open port: {e}")
            print("\nPort is locked by Motor Studio.")
            print("Use serial port monitor software instead!")
            return False
    return False

def create_capture_batch_script(port_name):
    """Create a Windows batch script for easier capture"""
    batch_content = f"""@echo off
echo ========================================
echo  Motor Studio Command Capture Helper
echo ========================================
echo.
echo Port: {port_name}
echo.
echo This script will help you capture Motor Studio commands.
echo.
echo INSTRUCTIONS:
echo   1. Download Free Serial Port Monitor
echo   2. Start monitoring {port_name}
echo   3. Open Motor Studio
echo   4. Connect to {port_name}
echo   5. Perform actions
echo   6. Export captured data
echo.
echo Press any key to open Serial Port Monitor download page...
pause >nul
start https://free-serial-port-monitor.com/
echo.
echo Once you have captured data, run:
echo   python analyze_captured_commands.py your_capture_file.csv
echo.
pause
"""
    
    with open('capture_commands.bat', 'w') as f:
        f.write(batch_content)
    
    print("Created capture_commands.bat")
    print("  Run this batch file for instructions")

def main():
    print("="*70)
    print("  AUTOMATED MOTOR STUDIO COMMAND CAPTURE")
    print("="*70)
    print()
    
    # Find COM ports
    print("Scanning for COM ports...")
    ports = find_com_ports()
    
    if not ports:
        print("No COM ports found!")
        print("\nMake sure USB-to-CAN adapter is connected to Windows.")
        return
    
    print(f"Found {len(ports)} COM port(s):")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port}")
    print()
    
    # Select port
    if len(ports) == 1:
        port_name = ports[0]
        print(f"Using port: {port_name}")
    else:
        port_num = input(f"Select port (1-{len(ports)}): ").strip()
        try:
            port_name = ports[int(port_num) - 1]
        except:
            print("Invalid selection")
            return
    
    print()
    print("="*70)
    print("  CAPTURE METHOD")
    print("="*70)
    print()
    print("Due to Windows COM port locking, choose a method:")
    print()
    print("1. Use Serial Port Monitor Software (RECOMMENDED)")
    print("   - Works alongside Motor Studio")
    print("   - Captures all traffic")
    print("   - Requires external software")
    print()
    print("2. Try Direct Capture (Likely to fail)")
    print("   - Attempts to open port directly")
    print("   - Will fail if Motor Studio is using port")
    print("   - May work if Motor Studio closes port temporarily")
    print()
    print("3. Create Helper Batch Script")
    print("   - Creates instructions file")
    print("   - Opens download page")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        print("\n" + "="*70)
        print("  SERIAL PORT MONITOR METHOD")
        print("="*70)
        print()
        print("1. Download Free Serial Port Monitor:")
        print("   https://free-serial-port-monitor.com/")
        print()
        print("2. Install and run it")
        print()
        print(f"3. Start monitoring: {port_name}")
        print()
        print("4. Open Motor Studio and connect to:", port_name)
        print()
        print("5. Perform actions (scan, enable, move motors)")
        print()
        print("6. Export captured data as CSV")
        print()
        print("7. Analyze with:")
        print("   python analyze_captured_commands.py <captured_file.csv>")
        print()
        
        # Try to open download page
        try:
            import webbrowser
            open_browser = input("Open download page in browser? (y/n): ").strip().lower()
            if open_browser == 'y':
                webbrowser.open('https://free-serial-port-monitor.com/')
        except:
            pass
    
    elif choice == '2':
        print("\n" + "="*70)
        print("  DIRECT CAPTURE ATTEMPT")
        print("="*70)
        print()
        
        # Check if port is available
        if check_port_available(port_name):
            print(f"Port {port_name} is currently available")
            print()
            print("Starting capture...")
            print("Note: Motor Studio cannot use this port while we're capturing")
            print("Press Ctrl+C to stop")
            print()
            
            try:
                ser = serial.Serial(port_name, 921600, timeout=0.1)
                capture_file = f'motor_studio_capture_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                
                with open(capture_file, 'w') as f:
                    packet_count = 0
                    try:
                        while True:
                            if ser.in_waiting > 0:
                                data = ser.read(ser.in_waiting)
                                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                packet_count += 1
                                
                                hex_str = data.hex(' ')
                                line = f"[{timestamp}] {hex_str}\n"
                                print(f"[{timestamp}] {hex_str}")
                                f.write(line)
                                f.flush()
                            
                            time.sleep(0.01)
                    except KeyboardInterrupt:
                        print(f"\n\nCaptured {packet_count} packets")
                        print(f"Saved to: {capture_file}")
                        print(f"\nAnalyze with:")
                        print(f"  python analyze_captured_commands.py {capture_file}")
                
                ser.close()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"Port {port_name} is locked (probably by Motor Studio)")
            print()
            print("Cannot capture directly. Use serial port monitor software!")
            capture_with_motor_studio_instructions(port_name)
    
    elif choice == '3':
        create_capture_batch_script(port_name)
    
    print()
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

