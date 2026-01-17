#!/usr/bin/env python3
"""
Test Motor 2 with correct AT protocol format
Based on working quick_motor_test.py
"""
import serial
import sys
import time

def build_activate_cmd(can_id):
    """Build motor activation command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    """Build motor deactivation command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    """Build load parameters command"""
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_move_jog_cmd(can_id, speed=0.0, flag=1):
    """Build jog movement command"""
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = int(0x8000 + (speed * 3283.0))
    else:
        speed_val = int(0x7fff + (speed * 3283.0))
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, flag])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def send_command(ser, cmd, description=""):
    """Send command and show response"""
    if description:
        print(f"  {description}")
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)
    
    # Check for response
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"    Response: {response.hex()}")
        return response
    return None

def scan_for_motor2(ser):
    """Scan for Motor 2 in expected range"""
    print("\n" + "=" * 70)
    print("  SCANNING FOR MOTOR 2 (IDs 16-20)")
    print("=" * 70 + "\n")
    
    # Send detection command first
    detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])  # AT+AT
    print("Sending AT+AT detection command...")
    ser.write(detect_cmd)
    ser.flush()
    time.sleep(0.3)
    response = ser.read(100)
    if response:
        print(f"  Adapter response: {response.decode('utf-8', errors='ignore').strip()}\n")
    
    found = []
    
    for can_id in range(16, 21):
        print(f"Testing ID {can_id} (0x{can_id:02X})...", end=" ", flush=True)
        
        # Try to activate
        ser.reset_input_buffer()
        cmd = build_activate_cmd(can_id)
        ser.write(cmd)
        ser.flush()
        time.sleep(0.2)
        
        # Check for response
        response = ser.read(100)
        if response and len(response) > 0:
            print(f"✅ FOUND!")
            print(f"  Response: {response.hex()}")
            found.append(can_id)
            
            # Deactivate it
            ser.write(build_deactivate_cmd(can_id))
            time.sleep(0.1)
        else:
            print("No response")
        
        time.sleep(0.1)
    
    print("\n" + "=" * 70)
    if found:
        print(f"✅ Found motor(s) at ID(s): {found}")
        return found[0]
    else:
        print("❌ No motors found in range 16-20")
        return None

def test_motor2(ser, can_id):
    """Test Motor 2 with movement"""
    print("\n" + "=" * 70)
    print(f"  TESTING MOTOR 2 (ID {can_id})")
    print("=" * 70 + "\n")
    
    # Test 1: Activate
    print("Test 1: Activating motor...")
    response = send_command(ser, build_activate_cmd(can_id), "  Sending activate command")
    if response:
        print("  ✅ Motor activated\n")
    else:
        print("  ⚠️  No response\n")
    
    time.sleep(0.2)
    
    # Test 2: Load parameters
    print("Test 2: Loading parameters...")
    response = send_command(ser, build_load_params_cmd(can_id), "  Sending load params command")
    if response:
        print("  ✅ Parameters loaded\n")
    else:
        print("  ⚠️  No response\n")
    
    time.sleep(0.2)
    
    # Test 3: Movement test (3 pulses)
    print("Test 3: Movement test (3 pulses)...")
    print("  Watch Motor 2 - it should move!\n")
    
    for i in range(3):
        print(f"  Pulse {i+1}/3...")
        
        # Move forward
        send_command(ser, build_move_jog_cmd(can_id, 0.08, 1))
        time.sleep(0.4)
        
        # Stop
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.3)
    
    print("  ✅ Movement test complete\n")
    
    # Test 4: Deactivate
    print("Test 4: Deactivating motor...")
    response = send_command(ser, build_deactivate_cmd(can_id), "  Sending deactivate command")
    if response:
        print("  ✅ Motor deactivated\n")
    else:
        print("  ⚠️  No response\n")
    
    print("=" * 70)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 70)

def main():
    print("\n🤖 Motor 2 Test - Correct AT Protocol\n")
    
    port = '/dev/ttyUSB1'
    baudrate = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    
    print(f"Configuration:")
    print(f"  Port: {port}")
    print(f"  Baudrate: {baudrate}")
    print(f"  Protocol: AT command format\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"✓ Connected to {port}\n")
        time.sleep(0.5)
        
        # Step 1: Scan for Motor 2
        motor_id = scan_for_motor2(ser)
        
        if motor_id:
            # Step 2: Test Motor 2
            test_motor2(ser, motor_id)
        else:
            print("\n❌ Could not find Motor 2")
            print("\nTroubleshooting:")
            print("  1. Check motor power (LED should be on)")
            print("  2. Verify CAN wiring (CAN-H, CAN-L, GND)")
            print("  3. Check 120Ω termination resistor")
            print("  4. Try different baudrate:")
            print(f"     python3 test_motor2_correct_protocol.py {port} 115200")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
        print(f"\nCheck:")
        print(f"  1. Port exists: ls -la {port}")
        print(f"  2. Permissions: sudo usermod -a -G dialout $USER")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

