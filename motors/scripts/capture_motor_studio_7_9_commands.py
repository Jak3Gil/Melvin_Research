#!/usr/bin/env python3
"""
Capture Motor Studio's exact commands when detecting Motors 7 and 9 individually
Then we can replay those commands when all motors are connected
"""
import serial
import time

def monitor_commands(ser, duration=30):
    """Monitor and capture all commands from Motor Studio"""
    print(f"Monitoring for {duration} seconds...")
    print("Run Motor Studio detection now!")
    print()
    
    commands_captured = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            if len(data) >= 4:
                hex_str = data.hex()
                commands_captured.append(hex_str)
                print(f"Captured: {hex_str}")
        
        time.sleep(0.1)
    
    return commands_captured

port = 'COM6'
print("="*70)
print("Capture Motor Studio Commands for Motors 7 and 9")
print("="*70)
print()
print("INSTRUCTIONS:")
print("1. Make sure ONLY Motors 7 and 9 are connected")
print("2. Open Motor Studio and let it detect the motors")
print("3. This script will capture all commands Motor Studio sends")
print()
print("Starting monitoring in 5 seconds...")
print("Then start Motor Studio detection!")
time.sleep(5)
print()

try:
    ser = serial.Serial(port, 921600, timeout=1.0)
    time.sleep(0.5)
    
    # Monitor for 30 seconds
    commands = monitor_commands(ser, duration=30)
    
    ser.close()
    
    print()
    print("="*70)
    print("CAPTURED COMMANDS")
    print("="*70)
    print()
    
    if commands:
        print(f"Total commands captured: {len(commands)}")
        print()
        print("Commands:")
        for i, cmd in enumerate(commands, 1):
            print(f"  {i}. {cmd}")
    else:
        print("No commands captured. Make sure Motor Studio is sending data.")
    
    print()
    print("="*70)
    print()
    print("Next step: Replay these commands when all motors are connected")
    print("to see if they activate Motors 7 and 9 in the combined state.")
    print()
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

