#!/usr/bin/env python3
"""
Replicate Motor Studio's device detection process:
1. Open serial port
2. Enable multi-device enablement
3. Detect devices
4. Scan for motors
"""
import serial
import struct
import time
import sys

def enable_multi_device(ser):
    """Enable multi-device mode (Motor Studio step 2)"""
    print("Step 2: Enabling multi-device mode...")
    
    # Try different possible commands for multi-device enablement
    multi_device_commands = [
        ("AT+MD", b"AT+MD\r\n"),  # Multi-device
        ("AT MD", b"AT MD\r\n"),
        ("AT+MULTI", b"AT+MULTI\r\n"),
        ("AT ENABLE MULTI", b"AT ENABLE MULTI\r\n"),
        ("AT+ENABLE", b"AT+ENABLE\r\n"),
        # CANopen NMT broadcast to enable all nodes
        ("NMT Start All", create_nmt_broadcast(0x01)),  # Start all nodes
        ("NMT Pre-op All", create_nmt_broadcast(0x80)),  # Pre-operational all
    ]
    
    for cmd_name, cmd_bytes in multi_device_commands:
        print(f"  Trying: {cmd_name}")
        if isinstance(cmd_bytes, bytes):
            ser.write(cmd_bytes)
        else:
            # It's a CAN frame
            ser.write(cmd_bytes)
        time.sleep(0.2)
        response = ser.read(100)
        if response:
            print(f"    Response: {response.hex()[:40]}...")
            return True
    
    print("  [X] No clear response, continuing anyway...")
    return False

def create_nmt_broadcast(command):
    """Create CANopen NMT broadcast command"""
    # NMT COB-ID: 0x000, data: [command, 0x00] (0x00 = all nodes)
    packet = bytearray([0xAA, 0x55])  # Frame header
    packet.extend(struct.pack('<I', 0x000)[:4])  # NMT COB-ID
    packet.append(2)  # DLC
    packet.extend([command, 0x00])  # Command + broadcast (0x00 = all)
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    return packet

def detect_devices(ser):
    """Detect devices (Motor Studio step 3)"""
    print("\nStep 3: Detecting devices...")
    
    # Try different device detection commands
    detect_commands = [
        ("AT+DETECT", b"AT+DETECT\r\n"),
        ("AT DETECT", b"AT DETECT\r\n"),
        ("AT+SCAN", b"AT+SCAN\r\n"),
        ("AT SCAN", b"AT SCAN\r\n"),
        ("AT+LIST", b"AT+LIST\r\n"),
        ("AT LIST", b"AT LIST\r\n"),
        # CANopen node guarding or heartbeat request
        ("NMT Node Guard", create_node_guard_request()),
        # Broadcast SDO read to find nodes
        ("SDO Broadcast", create_sdo_broadcast()),
    ]
    
    found_devices = []
    
    for cmd_name, cmd_bytes in detect_commands:
        print(f"  Trying: {cmd_name}")
        if isinstance(cmd_bytes, bytes):
            ser.write(cmd_bytes)
        else:
            ser.write(cmd_bytes)
        
        time.sleep(0.5)  # Give devices time to respond
        
        # Read all responses
        responses = []
        start_time = time.time()
        while time.time() - start_time < 2.0:  # Collect responses for 2 seconds
            response = ser.read(100)
            if response and len(response) > 0:
                responses.append(response)
                print(f"    Response {len(responses)}: {response.hex()[:60]}...")
            time.sleep(0.1)
        
        if responses:
            found_devices.extend(responses)
            print(f"    [OK] Got {len(responses)} response(s)")
            break
    
    return found_devices

def create_node_guard_request():
    """Create CANopen node guard request (broadcast)"""
    # Node guard COB-ID: 0x700 + node_id, but we'll try broadcast
    packet = bytearray([0xAA, 0x55])
    # Try 0x700 (emergency) or 0x180 (RPDO) broadcast
    packet.extend(struct.pack('<I', 0x700)[:4])  # Emergency COB-ID
    packet.append(0)  # DLC
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    return packet

def create_sdo_broadcast():
    """Create SDO broadcast read request"""
    packet = bytearray([0xAA, 0x55])
    # SDO request to node 0 (broadcast) - 0x600 + 0 = 0x600
    packet.extend(struct.pack('<I', 0x600)[:4])
    packet.append(4)  # DLC
    # SDO read: 0x40 (read 4 bytes), index 0x1000 (device type), subindex 0
    packet.extend([0x40, 0x00, 0x10, 0x00])
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    return packet

def scan_individual_motors(ser, motor_ids):
    """Scan individual motors after detection"""
    print(f"\nStep 4: Scanning individual motors {motor_ids}...")
    
    found = []
    for motor_id in motor_ids:
        print(f"  Testing Motor {motor_id}...")
        
        # Try SDO read to get device info
        extended_id = 0x600 + motor_id
        data = bytearray([0x40, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00])  # Read device type
        
        packet = bytearray([0xAA, 0x55])
        packet.extend(struct.pack('<I', extended_id)[:4])
        packet.append(len(data))
        packet.extend(data)
        checksum = sum(packet[2:]) & 0xFF
        packet.append(checksum)
        
        ser.write(packet)
        time.sleep(0.2)
        response = ser.read(100)
        
        if response and len(response) > 0:
            print(f"    [OK] Motor {motor_id} responded: {response.hex()[:60]}...")
            found.append((motor_id, response))
        else:
            print(f"    [X] No response")
    
    return found

def main():
    port = 'COM3'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print("="*60)
    print("Motor Studio Device Detection Replication")
    print("="*60)
    print(f"Port: {port}")
    print("Baudrate: 921600")
    print("="*60)
    print()
    
    try:
        # Step 1: Open serial port
        print("Step 1: Opening serial port...")
        ser = serial.Serial(port, 921600, timeout=1.0)
        print(f"[OK] Connected to {port}")
        time.sleep(0.5)  # Let port stabilize
        
        # Step 2: Enable multi-device mode
        enable_multi_device(ser)
        time.sleep(0.5)
        
        # Step 3: Detect devices
        devices = detect_devices(ser)
        
        if devices:
            print(f"\n[OK] Found {len(devices)} device response(s)!")
            print("\nDevice responses:")
            for i, dev in enumerate(devices, 1):
                print(f"  Device {i}: {dev.hex()[:80]}...")
        else:
            print("\n[X] No devices detected automatically")
            print("Trying individual motor scan...")
            
            # Step 4: Try scanning known motors
            known_motors = [5, 6, 7, 10, 11, 12, 13, 14]
            found = scan_individual_motors(ser, known_motors)
            
            if found:
                print(f"\n[OK] Found {len(found)} motor(s):")
                for motor_id, response in found:
                    print(f"  Motor {motor_id}: {response.hex()[:60]}...")
        
        ser.close()
        print("\n[OK] Scan complete!")
        
    except serial.SerialException as e:
        print(f"\n[X] Cannot open {port}: {e}")
        print("Please close Motor Studio and try again.")
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

