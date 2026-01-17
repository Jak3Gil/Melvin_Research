#!/usr/bin/env python3
"""
RobStride Motor OTA Firmware Updater - SocketCAN Version
Uses direct CAN interface (can0/can1) with extended 29-bit IDs

This version works with the official RobStride motor controller!
"""

import can
import sys
import time
import struct
import os

# OTA Protocol Frame Types (29-bit CAN ID format)
FRAME_GET_DEVICE_ID = 0    # Get device ID and MCU unique identifier
FRAME_UPGRADE_START = 11   # Start upgrade
FRAME_UPGRADE_INFO = 12    # Send bin file info (size, packet count)
FRAME_UPGRADE_DATA = 13    # Send data packets

HOST_CAN_ID = 0x7F  # Our host CAN ID

def build_29bit_can_id(frame_type, host_id, target_id):
    """
    Build 29-bit CAN ID for OTA protocol
    Bit28~24: frame_type
    Bit23~16: reserved (0)
    Bit15~8: host CAN ID
    Bit7~0: target motor CAN ID
    """
    can_id = (frame_type << 24) | (host_id << 8) | target_id
    return can_id

def send_can_message(bus, can_id, data, wait_response=True, timeout=1.0):
    """Send CAN message and optionally wait for response"""
    msg = can.Message(
        arbitration_id=can_id,
        data=data,
        is_extended_id=True,  # Use 29-bit extended IDs
        is_fd=False
    )
    
    try:
        bus.send(msg)
        print(f"  → Sent: ID=0x{can_id:08X}, Data={data.hex()}")
        
        if wait_response:
            response = bus.recv(timeout=timeout)
            if response:
                print(f"  ← Recv: ID=0x{response.arbitration_id:08X}, Data={response.data.hex()}")
                return response
            else:
                print(f"  ✗ No response (timeout {timeout}s)")
                return None
        return True
        
    except Exception as e:
        print(f"  ✗ Error sending: {e}")
        return None

def get_device_id(bus, motor_id):
    """Get device ID and MCU unique identifier"""
    can_id = build_29bit_can_id(FRAME_GET_DEVICE_ID, HOST_CAN_ID, motor_id)
    data = bytes([0x00] * 8)
    
    response = send_can_message(bus, can_id, data, wait_response=True, timeout=1.0)
    
    if response:
        # Response format: [device_id, mcu_unique_id (12 bytes)]
        device_id = response.data[0] if len(response.data) > 0 else None
        return device_id
    return None

def start_upgrade(bus, motor_id):
    """Send upgrade start command"""
    can_id = build_29bit_can_id(FRAME_UPGRADE_START, HOST_CAN_ID, motor_id)
    data = bytes([0x01] + [0x00] * 7)  # Start upgrade
    
    response = send_can_message(bus, can_id, data, wait_response=True, timeout=2.0)
    return response is not None

def send_file_info(bus, motor_id, file_size, packet_count):
    """Send firmware file information"""
    can_id = build_29bit_can_id(FRAME_UPGRADE_INFO, HOST_CAN_ID, motor_id)
    
    # Pack file size (4 bytes) and packet count (4 bytes)
    data = struct.pack('<II', file_size, packet_count)
    
    response = send_can_message(bus, can_id, data, wait_response=True, timeout=2.0)
    return response is not None

def send_data_packet(bus, motor_id, packet_num, packet_data):
    """Send a single data packet"""
    can_id = build_29bit_can_id(FRAME_UPGRADE_DATA, HOST_CAN_ID, motor_id)
    
    # Pack packet number (2 bytes) + data (6 bytes max per CAN frame)
    data = struct.pack('<H', packet_num) + packet_data[:6]
    data = data.ljust(8, b'\x00')  # Pad to 8 bytes
    
    response = send_can_message(bus, can_id, data, wait_response=False)
    return response is not None

def update_firmware(bus, motor_id, firmware_path):
    """Main firmware update function"""
    print(f"\n{'='*60}")
    print(f"  Firmware Update: Motor CAN ID {motor_id}")
    print(f"{'='*60}\n")
    
    # Load firmware file
    if not os.path.exists(firmware_path):
        print(f"✗ Firmware file not found: {firmware_path}")
        return False
    
    with open(firmware_path, 'rb') as f:
        firmware_data = f.read()
    
    file_size = len(firmware_data)
    packet_size = 6  # 6 bytes per packet (CAN frame has 8 bytes, 2 for packet number)
    packet_count = (file_size + packet_size - 1) // packet_size
    
    print(f"✓ Firmware file loaded: {file_size} bytes")
    print(f"  Packets to send: {packet_count}\n")
    
    # Step 1: Get device ID
    print(f"[1/4] Getting device ID for motor {motor_id}...")
    device_id = get_device_id(bus, motor_id)
    
    if device_id is None:
        print(f"  ✗ No response from motor {motor_id}")
        print(f"\n✗ Failed to get device ID\n")
        return False
    
    print(f"  ✓ Device ID: {device_id}\n")
    
    # Step 2: Start upgrade
    print(f"[2/4] Starting upgrade mode...")
    if not start_upgrade(bus, motor_id):
        print(f"  ✗ Failed to start upgrade mode")
        return False
    
    print(f"  ✓ Upgrade mode started\n")
    time.sleep(0.5)
    
    # Step 3: Send file info
    print(f"[3/4] Sending file information...")
    if not send_file_info(bus, motor_id, file_size, packet_count):
        print(f"  ✗ Failed to send file info")
        return False
    
    print(f"  ✓ File info sent\n")
    time.sleep(0.5)
    
    # Step 4: Send data packets
    print(f"[4/4] Sending firmware data...")
    print(f"  Progress: ", end='', flush=True)
    
    for i in range(packet_count):
        offset = i * packet_size
        packet_data = firmware_data[offset:offset + packet_size]
        
        if not send_data_packet(bus, motor_id, i, packet_data):
            print(f"\n  ✗ Failed to send packet {i}")
            return False
        
        # Progress indicator
        if i % (packet_count // 20) == 0:
            print('.', end='', flush=True)
        
        time.sleep(0.01)  # Small delay between packets
    
    print(" Done!")
    print(f"  ✓ All {packet_count} packets sent\n")
    
    print(f"✓ Firmware update complete!")
    print(f"  Motor will reboot with new firmware...\n")
    
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 ota_firmware_updater_socketcan.py <can_interface> <firmware_file> [motor_id]")
        print("\nExample:")
        print("  python3 ota_firmware_updater_socketcan.py can0 rs00_0.0.3.22.bin 8")
        print("\nAvailable CAN interfaces:")
        os.system("ip link show | grep can")
        sys.exit(1)
    
    can_interface = sys.argv[1]
    firmware_file = sys.argv[2]
    motor_id = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    print("="*60)
    print("  RobStride Motor OTA Firmware Updater (SocketCAN)")
    print("="*60)
    print(f"\nCAN Interface: {can_interface}")
    print(f"Firmware: {firmware_file}")
    if motor_id:
        print(f"Target Motor: CAN ID {motor_id}")
    else:
        print(f"Target: All motors (broadcast)")
    
    print("\n" + "="*60)
    print("  ⚠️  CRITICAL WARNINGS")
    print("="*60)
    print("1. Ensure STABLE POWER to all motors")
    print("2. Do NOT interrupt the update process")
    print("3. Motor will be BRICKED if power is lost")
    print("4. Test on ONE motor first")
    print("5. Have a backup plan")
    print("\n" + "="*60 + "\n")
    
    response = input("Type 'YES' to continue (anything else to cancel): ")
    if response != 'YES':
        print("\n✗ Update cancelled by user\n")
        sys.exit(0)
    
    try:
        # Initialize CAN bus
        print(f"\nInitializing CAN bus {can_interface}...")
        bus = can.interface.Bus(channel=can_interface, bustype='socketcan')
        print(f"✓ CAN bus initialized\n")
        
        if motor_id:
            # Update single motor
            success = update_firmware(bus, motor_id, firmware_file)
        else:
            # Update all motors (use broadcast or scan)
            print("⚠️  Broadcast update not yet implemented")
            print("   Please specify a motor ID\n")
            success = False
        
        bus.shutdown()
        
        if success:
            print("\n" + "="*60)
            print("  ✅ FIRMWARE UPDATE SUCCESSFUL!")
            print("="*60)
            print("\nNext steps:")
            print("1. Power cycle the motor")
            print("2. Verify new firmware version")
            print("3. Test motor operation")
            print("4. Configure unique CAN ID if needed\n")
        else:
            print("\n✗ Firmware update failed!\n")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Update interrupted by user!")
        print("   Motor may be in inconsistent state")
        print("   Try updating again\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("[COMPLETE]\n")

if __name__ == "__main__":
    main()

