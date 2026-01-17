#!/usr/bin/env python3
"""
Test Motor 2 using broadcast commands
Broadcast should make ALL motors respond, revealing their IDs
"""
import serial
import sys
import time

def send_and_listen(ser, cmd, description, listen_time=1.0):
    """Send command and listen for all responses"""
    print(f"\n{description}")
    print(f"  Command: {cmd.hex()}")
    
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    
    print(f"  Listening for {listen_time}s...")
    
    responses = []
    start_time = time.time()
    
    while time.time() - start_time < listen_time:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            if data:
                responses.append(data)
                print(f"  📨 Response {len(responses)}: {data.hex()}")
                print(f"     ASCII: {data.decode('utf-8', errors='ignore')}")
        time.sleep(0.05)
    
    if not responses:
        print(f"  ⚠️  No responses")
    
    return responses

def test_broadcast_commands(port, baudrate):
    """Test various broadcast command formats"""
    print("=" * 70)
    print("  BROADCAST COMMAND TEST")
    print("=" * 70)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"\n✓ Connected to {port} at {baudrate} baud\n")
        
        # Send AT+AT first
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        print("Sending AT+AT detection command...")
        ser.write(detect_cmd)
        time.sleep(0.3)
        response = ser.read(100)
        if response:
            print(f"  Adapter: {response.decode('utf-8', errors='ignore').strip()}\n")
        
        print("=" * 70)
        print("Testing different broadcast methods...")
        print("=" * 70)
        
        all_responses = []
        
        # Test 1: Broadcast with ID 0 (AT protocol)
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0x00, 0x01, 0x00, 0x0d, 0x0a])
        responses = send_and_listen(ser, cmd, "Test 1: Broadcast ID 0 - Activate", 1.0)
        all_responses.extend(responses)
        time.sleep(0.3)
        
        # Test 2: Broadcast with ID 255 (AT protocol)
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0xFF, 0x01, 0x00, 0x0d, 0x0a])
        responses = send_and_listen(ser, cmd, "Test 2: Broadcast ID 255 - Activate", 1.0)
        all_responses.extend(responses)
        time.sleep(0.3)
        
        # Test 3: Broadcast with ID 127 (AT protocol)
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0x7F, 0x01, 0x00, 0x0d, 0x0a])
        responses = send_and_listen(ser, cmd, "Test 3: Broadcast ID 127 - Activate", 1.0)
        all_responses.extend(responses)
        time.sleep(0.3)
        
        # Test 4: Load params broadcast (ID 0)
        cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, 0x00, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        responses = send_and_listen(ser, cmd, "Test 4: Broadcast ID 0 - Load Params", 1.0)
        all_responses.extend(responses)
        time.sleep(0.3)
        
        # Test 5: Movement broadcast (ID 0) - small jog
        speed_val = 0x8100  # Small positive speed
        cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, 0x00, 0x08, 0x05, 0x70, 
                         0x00, 0x00, 0x07, 0x01])
        cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
        responses = send_and_listen(ser, cmd, "Test 5: Broadcast ID 0 - Movement", 1.5)
        all_responses.extend(responses)
        time.sleep(0.5)
        
        # Test 6: Stop movement (ID 0)
        cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, 0x00, 0x08, 0x05, 0x70, 
                         0x00, 0x00, 0x07, 0x00, 0x7f, 0xff, 0x0d, 0x0a])
        responses = send_and_listen(ser, cmd, "Test 6: Broadcast ID 0 - Stop", 1.0)
        all_responses.extend(responses)
        time.sleep(0.3)
        
        # Test 7: Deactivate broadcast (ID 0)
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        responses = send_and_listen(ser, cmd, "Test 7: Broadcast ID 0 - Deactivate", 1.0)
        all_responses.extend(responses)
        
        # Test 8: Listen for spontaneous messages
        print("\nTest 8: Passive listening (5 seconds)...")
        print("  Listening for any spontaneous motor messages...")
        ser.reset_input_buffer()
        start_time = time.time()
        msg_count = 0
        
        while time.time() - start_time < 5.0:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                msg_count += 1
                print(f"  📨 Message {msg_count}: {data.hex()}")
            time.sleep(0.1)
        
        if msg_count == 0:
            print(f"  ⚠️  No spontaneous messages")
        
        ser.close()
        
        # Summary
        print("\n" + "=" * 70)
        print("  SUMMARY")
        print("=" * 70)
        
        if all_responses:
            print(f"\n✅ Received {len(all_responses)} response(s)!")
            print("\nMotor(s) are connected and responding to broadcast!")
            print("\nNext step: Analyze responses to identify motor IDs")
        else:
            print("\n❌ NO RESPONSES to any broadcast commands")
            print("\nThis confirms:")
            print("  1. Motor is NOT powered")
            print("  2. CAN wiring is NOT connected")
            print("  3. Motor is on different port/adapter")
            print("\nPhysical checklist:")
            print("  ☐ Motor LED is ON")
            print("  ☐ Power supply connected (12-48V)")
            print("  ☐ CAN-H wire connected")
            print("  ☐ CAN-L wire connected")
            print("  ☐ Ground wire connected")
            print("  ☐ 120Ω termination resistor installed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_raw_can_broadcast(port, baudrate):
    """Test raw CAN broadcast (L91 protocol format)"""
    print("\n" + "=" * 70)
    print("  RAW CAN BROADCAST TEST (L91 Protocol)")
    print("=" * 70)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"\n✓ Connected\n")
        
        # L91 format broadcasts
        tests = [
            ("L91 Broadcast ID 0", bytearray([0xAA, 0x55, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 
                                              0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02])),
            ("L91 Broadcast ID 255", bytearray([0xAA, 0x55, 0x01, 0xFF, 0xFF, 0x00, 0x00, 0x00,
                                                0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])),
        ]
        
        for name, packet in tests:
            responses = send_and_listen(ser, bytes(packet), f"{name}", 1.0)
            time.sleep(0.3)
        
        ser.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n🔊 Motor 2 Broadcast Test\n")
    
    port = '/dev/ttyUSB1'
    baudrate = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    
    print(f"Configuration:")
    print(f"  Port: {port}")
    print(f"  Baudrate: {baudrate}")
    print(f"  Method: Broadcast commands to all motors\n")
    
    # Test AT protocol broadcasts
    test_broadcast_commands(port, baudrate)
    
    # Test L91 protocol broadcasts
    test_raw_can_broadcast(port, baudrate)
    
    print("\n" + "=" * 70)
    print("  BROADCAST TEST COMPLETE")
    print("=" * 70)
    print("\nIf no responses were received, Motor 2 is NOT connected to CAN bus.")

if __name__ == "__main__":
    main()



