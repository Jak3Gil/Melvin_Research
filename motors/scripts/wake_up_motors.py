#!/usr/bin/env python3
"""
Try to wake up motors with various initialization sequences
Maybe motors are in sleep/standby mode
"""

import serial
import time
import struct

def send_and_wait(ser, packet, description, wait_time=0.5):
    """Send packet and wait for response"""
    print(f"\n{description}")
    print(f"  Sending: {packet.hex(' ')}")
    
    ser.reset_input_buffer()
    ser.write(packet)
    ser.flush()
    time.sleep(wait_time)
    
    if ser.in_waiting > 0:
        resp = ser.read(ser.in_waiting)
        print(f"  ✅ Response: {len(resp)} bytes - {resp.hex(' ')}")
        return resp
    else:
        print(f"  ✗ No response")
        return None

print("="*70)
print("MOTOR WAKE-UP SEQUENCE TEST")
print("="*70)
print("\nTrying various initialization sequences...")
print("Maybe motors are in sleep/standby mode")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected to {port} at {baud} baud\n")
    
    # SEQUENCE 1: Reset/Init commands
    print("="*70)
    print("SEQUENCE 1: Reset/Initialization Commands")
    print("="*70)
    
    sequences = [
        (bytearray([0xFF, 0xFF, 0xFF, 0xFF]), "Reset sequence (0xFF x4)"),
        (bytearray([0x00, 0x00, 0x00, 0x00]), "Null sequence (0x00 x4)"),
        (bytearray([0xAA, 0x55]), "Sync bytes"),
        (bytearray([0x41, 0x54, 0x0d, 0x0a]), "AT command"),
        (bytearray([0x41, 0x54, 0x2b, 0x0d, 0x0a]), "AT+ command"),
        (bytearray([0x41, 0x54, 0x49, 0x0d, 0x0a]), "ATI command (identify)"),
    ]
    
    for packet, desc in sequences:
        resp = send_and_wait(ser, packet, desc, 0.3)
        if resp:
            print(f"  🎉 GOT RESPONSE! Motors may be waking up...")
            time.sleep(1)
            break
    
    # SEQUENCE 2: Broadcast enable to all possible IDs
    print("\n" + "="*70)
    print("SEQUENCE 2: Broadcast Enable (Multiple Attempts)")
    print("="*70)
    
    for attempt in range(5):
        print(f"\nAttempt {attempt + 1}/5...")
        
        # L91 AT broadcast
        packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x00])
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.extend([0x0d, 0x0a])
        
        resp = send_and_wait(ser, packet, f"  L91 AT Broadcast (attempt {attempt+1})", 0.5)
        
        if resp:
            print(f"  🎉 MOTORS RESPONDED!")
            break
        
        time.sleep(0.2)
    
    # SEQUENCE 3: Try enabling specific motor IDs with delays
    print("\n" + "="*70)
    print("SEQUENCE 3: Enable Specific IDs (Slow)")
    print("="*70)
    print("\nTrying IDs that worked before: 8, 16, 20, 24, 31, 32, 64, 72")
    
    test_ids = [8, 16, 20, 24, 31, 32, 64, 72]
    
    for motor_id in test_ids:
        # L91 AT protocol
        packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id])
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.extend([0x0d, 0x0a])
        
        resp = send_and_wait(ser, packet, f"  Enabling motor ID {motor_id}", 0.3)
        
        if resp:
            print(f"  🎉 MOTOR {motor_id} IS BACK!")
            
            # Try to scan around it
            print(f"\n  Scanning around ID {motor_id}...")
            for offset in range(-2, 3):
                test_id = motor_id + offset
                if 0 <= test_id <= 127:
                    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, test_id])
                    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                    packet.extend([0x0d, 0x0a])
                    
                    ser.write(packet)
                    ser.flush()
                    time.sleep(0.1)
                    
                    if ser.in_waiting > 0:
                        resp = ser.read(ser.in_waiting)
                        print(f"    ✓ ID {test_id}")
            break
    
    # SEQUENCE 4: Different baud rates with wake-up
    print("\n" + "="*70)
    print("SEQUENCE 4: Try Different Baud Rates")
    print("="*70)
    
    baud_rates = [115200, 230400, 460800, 921600, 1000000]
    
    for test_baud in baud_rates:
        print(f"\nTrying {test_baud} baud...")
        
        try:
            ser.close()
            ser = serial.Serial(port, test_baud, timeout=0.5)
            time.sleep(0.3)
            
            # Send wake-up + enable to ID 8
            packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x08])
            packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            packet.extend([0x0d, 0x0a])
            
            ser.write(packet)
            ser.flush()
            time.sleep(0.3)
            
            if ser.in_waiting > 0:
                resp = ser.read(ser.in_waiting)
                print(f"  ✅ MOTOR RESPONDS AT {test_baud} BAUD!")
                print(f"     Response: {resp.hex(' ')}")
                
                # Found working baud, do full scan
                print(f"\n  Running full scan at {test_baud}...")
                found = []
                
                for test_id in range(0, 128, 4):
                    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, test_id])
                    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                    packet.extend([0x0d, 0x0a])
                    
                    ser.write(packet)
                    ser.flush()
                    time.sleep(0.05)
                    
                    if ser.in_waiting > 0:
                        ser.read(ser.in_waiting)
                        found.append(test_id)
                
                if found:
                    print(f"  ✅ Found motors at IDs: {found}")
                
                break
            else:
                print(f"  ✗ No response at {test_baud}")
                
        except Exception as e:
            print(f"  ✗ Error at {test_baud}: {e}")
    
    # SEQUENCE 5: Power cycle detection
    print("\n" + "="*70)
    print("SEQUENCE 5: Continuous Monitoring")
    print("="*70)
    print("\n⚠️  If motors still not responding:")
    print("   1. Leave this script running")
    print("   2. Power cycle the motors")
    print("   3. Watch for responses")
    print("\nMonitoring for 30 seconds...")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Return to 921600
        if ser.baudrate != 921600:
            ser.close()
            ser = serial.Serial(port, 921600, timeout=0.5)
            time.sleep(0.3)
        
        start_time = time.time()
        scan_count = 0
        
        while time.time() - start_time < 30:
            # Quick scan of known IDs
            for test_id in [8, 16, 20, 24, 31, 32, 64, 72]:
                packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, test_id])
                packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                packet.extend([0x0d, 0x0a])
                
                ser.write(packet)
                ser.flush()
                time.sleep(0.05)
                
                if ser.in_waiting > 0:
                    resp = ser.read(ser.in_waiting)
                    print(f"[{time.time()-start_time:.1f}s] ✅ Motor ID {test_id} responded!")
                    print(f"  Response: {resp.hex(' ')}")
                    print(f"\n🎉 MOTORS ARE BACK ONLINE!\n")
                    ser.close()
                    exit(0)
            
            scan_count += 1
            if scan_count % 10 == 0:
                print(f"[{time.time()-start_time:.1f}s] Still monitoring... (scan #{scan_count})")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print(f"\n\nMonitoring stopped by user")
    
    ser.close()
    
    print("\n" + "="*70)
    print("FINAL STATUS")
    print("="*70)
    print("\n❌ Motors still not responding")
    print("\n🔧 REQUIRED ACTIONS:")
    print("\n1. PHYSICAL CHECK:")
    print("   - Verify motor power LEDs are ON")
    print("   - Check CAN-H and CAN-L wiring")
    print("   - Verify 120Ω termination resistors")
    print("\n2. POWER CYCLE:")
    print("   - Turn OFF motor power supply")
    print("   - Wait 10 seconds")
    print("   - Turn ON motor power supply")
    print("   - Run this script again immediately")
    print("\n3. TEST ONE MOTOR:")
    print("   - Disconnect all motors except ONE")
    print("   - Connect just that motor to USB-CAN adapter")
    print("   - Add 120Ω terminator")
    print("   - Run this script")
    print("\n4. CHECK ADAPTER:")
    print("   - Is the USB-CAN adapter the correct model?")
    print("   - Does it need drivers/configuration?")
    print("   - Try different USB port on Jetson")
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

