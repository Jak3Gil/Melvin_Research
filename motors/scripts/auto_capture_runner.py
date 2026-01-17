#!/usr/bin/env python3
"""
Fully Automated Motor Studio Capture Helper
Non-interactive version that runs automatically
"""
import serial
import serial.tools.list_ports
import os
import sys
from datetime import datetime

def find_ports():
    """Find all COM ports"""
    return [port.device for port in serial.tools.list_ports.comports()]

def check_port_available(port_name):
    """Check if port can be opened"""
    try:
        ser = serial.Serial(port_name, 921600, timeout=0.1)
        ser.close()
        return True
    except:
        return False

def create_instructions_file(ports, available_ports):
    """Create an instructions file automatically"""
    instructions = f"""MOTOR STUDIO COMMAND CAPTURE - AUTOMATED INSTRUCTIONS
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

AVAILABLE COM PORTS:
"""
    for i, port in enumerate(ports, 1):
        status = "AVAILABLE" if port in available_ports else "LOCKED (probably Motor Studio)"
        instructions += f"  {i}. {port} - {status}\n"
    
    instructions += f"""
RECOMMENDED PORT: {available_ports[0] if available_ports else ports[0] if ports else 'NONE'}

AUTOMATED CAPTURE INSTRUCTIONS:
================================

Since Windows locks COM ports, you need to use serial port monitor software.

STEP 1: Download Serial Port Monitor
  URL: https://free-serial-port-monitor.com/
  (Free trial available)

STEP 2: Install and Run Serial Port Monitor
  - Install the software
  - Launch it

STEP 3: Start Monitoring
  - Port: {available_ports[0] if available_ports else ports[0] if ports else 'COM?'}
  - Baud: 921600
  - Data bits: 8
  - Stop bits: 1
  - Parity: None

STEP 4: Open Motor Studio
  - Launch motor_tool.exe
  - Connect to the same port
  - Motor Studio and monitor can both use the port!

STEP 5: Perform Actions
  - Scan for motors
  - Enable a motor
  - Move a motor
  - Each action generates commands

STEP 6: Export Captured Data
  - Select all captured commands
  - Export as CSV format
  - Save as: motor_studio_capture.csv

STEP 7: Analyze Commands
  Run: python analyze_captured_commands.py motor_studio_capture.csv

ALTERNATIVE: Direct Capture (if Motor Studio is NOT running)
  Run: python capture_motor_studio_commands.py
  (Will only work if port is not locked)

NEXT STEPS:
===========

1. If Motor Studio is running:
   - Use Serial Port Monitor (see above)
   - This is the only reliable method

2. If Motor Studio is NOT running:
   - Port should be available
   - But Motor Studio needs to be running to send commands!
   - So this doesn't help much...

3. Best Solution:
   - Use Serial Port Monitor software
   - It works alongside Motor Studio
   - No port locking issues
"""
    
    with open('CAPTURE_INSTRUCTIONS.txt', 'w') as f:
        f.write(instructions)
    
    print(f"Instructions saved to: CAPTURE_INSTRUCTIONS.txt")
    return instructions

def main():
    print("="*70)
    print("  AUTOMATED MOTOR STUDIO CAPTURE HELPER")
    print("="*70)
    print()
    
    # Find ports
    print("Scanning for COM ports...")
    ports = find_ports()
    
    if not ports:
        print("No COM ports found!")
        print("\nMake sure USB-to-CAN adapter is connected to Windows.")
        return
    
    print(f"Found {len(ports)} COM port(s):")
    for port in ports:
        print(f"  - {port}")
    print()
    
    # Check availability
    print("Checking port availability...")
    available_ports = []
    locked_ports = []
    
    for port in ports:
        if check_port_available(port):
            available_ports.append(port)
            print(f"  {port}: AVAILABLE")
        else:
            locked_ports.append(port)
            print(f"  {port}: LOCKED (probably Motor Studio)")
    
    print()
    
    # Create instructions
    print("Generating instructions...")
    instructions = create_instructions_file(ports, available_ports)
    
    print()
    print("="*70)
    print("  RESULTS")
    print("="*70)
    print()
    
    if locked_ports:
        print(f"Motor Studio appears to be running on: {', '.join(locked_ports)}")
        print()
        print("RECOMMENDATION:")
        print("  Use Serial Port Monitor software to capture commands")
        print("  (See CAPTURE_INSTRUCTIONS.txt for details)")
        print()
    
    if available_ports:
        print(f"Available ports: {', '.join(available_ports)}")
        print()
        print("NOTE:")
        print("  Even though ports are available, Motor Studio needs to be")
        print("  running to send commands. Use Serial Port Monitor instead.")
        print()
    
    # Try to open browser with instructions
    print("Opening capture instructions file...")
    try:
        os.startfile('CAPTURE_INSTRUCTIONS.txt')
    except:
        try:
            subprocess.run(['notepad', 'CAPTURE_INSTRUCTIONS.txt'])
        except:
            print("(Could not open file automatically)")
    
    print()
    print("="*70)
    print()
    print("NEXT ACTION:")
    print("  1. Read CAPTURE_INSTRUCTIONS.txt")
    print("  2. Download Serial Port Monitor")
    print("  3. Capture Motor Studio commands")
    print("  4. Analyze with: python analyze_captured_commands.py <capture_file.csv>")
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

