#!/usr/bin/env python3
"""
RobStride Motor OTA Firmware Updater
AUTOMATIC firmware update via CAN bus using OTA protocol

WARNING: This can brick motors if interrupted!
- Ensure stable power supply
- Don't interrupt the process
- Test on ONE motor first
- Have backup plan

Based on: OTA Agreement Description - EN_20251114102200.pdf
"""

import serial
import sys
import time
import struct

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

def send_l91_command(ser, cmd):
    """Send L91 protocol command"""
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.05)

def send_l91_with_response(ser, cmd, timeout=0.5):
    """Send L91 command and get response"""
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.05)
    
    response = b""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
        time.sleep(0.01)
    return response

def get_device_id(ser, target_can_id):
    """
    Frame Type 0: Get Device ID
    Request 64-bit MCU unique identifier
    """
    print(f"\n[1/4] Getting device ID for motor {target_can_id}...")
    
    # Build 29-bit CAN ID
    can_id_29bit = build_29bit_can_id(FRAME_GET_DEVICE_ID, HOST_CAN_ID, target_can_id)
    
    # L91 format: AT <cmd> <addr_high> <addr_low> <can_id> <data> \r\n
    # For 29-bit CAN ID, we need to encode it properly
    # Using extended frame format
    cmd = bytearray([0x41, 0x54])  # AT
    cmd.append(0x00)  # Command byte
    cmd.extend([(can_id_29bit >> 16) & 0xFF, (can_id_29bit >> 8) & 0xFF])  # Address
    cmd.append(can_id_29bit & 0xFF)  # CAN ID
    cmd.extend([0x00] * 8)  # 8 bytes of zeros
    cmd.extend([0x0d, 0x0a])  # \r\n
    
    response = send_l91_with_response(ser, bytes(cmd), timeout=1.0)
    
    if response and len(response) >= 8:
        print(f"  ✓ Device ID received: {response.hex(' ')}")
        return response[-8:]  # Last 8 bytes = 64-bit MCU ID
    else:
        print(f"  ✗ No response from motor {target_can_id}")
        return None

def send_upgrade_start(ser, target_can_id, mcu_id):
    """
    Frame Type 11: Upgrade Start
    Send 64-bit MCU unique identifier to start upgrade
    """
    print(f"\n[2/4] Starting upgrade for motor {target_can_id}...")
    
    can_id_29bit = build_29bit_can_id(FRAME_UPGRADE_START, HOST_CAN_ID, target_can_id)
    
    cmd = bytearray([0x41, 0x54])  # AT
    cmd.append(0x0B)  # Command byte (11)
    cmd.extend([(can_id_29bit >> 16) & 0xFF, (can_id_29bit >> 8) & 0xFF])
    cmd.append(can_id_29bit & 0xFF)
    cmd.extend(mcu_id)  # 8 bytes MCU ID
    cmd.extend([0x0d, 0x0a])
    
    response = send_l91_with_response(ser, bytes(cmd), timeout=2.0)
    
    if response:
        # Check response: Bit23~16 should be 0x00 for success
        print(f"  Response: {response.hex(' ')}")
        if len(response) > 3 and response[2] == 0x00:
            print(f"  ✓ Upgrade start accepted")
            return True
        else:
            print(f"  ✗ Upgrade start failed")
            return False
    else:
        print(f"  ✗ No response")
        return False

def send_upgrade_info(ser, target_can_id, bin_size, packet_count):
    """
    Frame Type 12: Upgrade Info
    Send bin file size and packet count
    """
    print(f"\n[3/4] Sending upgrade info...")
    print(f"  Bin size: {bin_size} bytes")
    print(f"  Packets: {packet_count}")
    
    can_id_29bit = build_29bit_can_id(FRAME_UPGRADE_INFO, HOST_CAN_ID, target_can_id)
    
    cmd = bytearray([0x41, 0x54])  # AT
    cmd.append(0x0C)  # Command byte (12)
    cmd.extend([(can_id_29bit >> 16) & 0xFF, (can_id_29bit >> 8) & 0xFF])
    cmd.append(can_id_29bit & 0xFF)
    
    # Data: Byte0~3 = bin_size (little endian), Byte4~7 = packet_count (little endian)
    cmd.extend(struct.pack('<I', bin_size))  # 4 bytes bin size
    cmd.extend(struct.pack('<I', packet_count))  # 4 bytes packet count
    cmd.extend([0x0d, 0x0a])
    
    response = send_l91_with_response(ser, bytes(cmd), timeout=1.0)
    
    if response and len(response) > 3 and response[2] == 0x00:
        print(f"  ✓ Upgrade info accepted")
        return True
    else:
        print(f"  ✗ Upgrade info failed")
        return False

def send_upgrade_data(ser, target_can_id, firmware_data, packet_size=8):
    """
    Frame Type 13: Upgrade Data
    Send firmware data in packets
    """
    print(f"\n[4/4] Sending firmware data...")
    
    total_bytes = len(firmware_data)
    packet_count = (total_bytes + packet_size - 1) // packet_size
    
    print(f"  Total: {total_bytes} bytes in {packet_count} packets")
    print(f"  This will take approximately {packet_count * 0.1:.1f} seconds")
    print()
    
    can_id_29bit = build_29bit_can_id(FRAME_UPGRADE_DATA, HOST_CAN_ID, target_can_id)
    
    for packet_num in range(packet_count):
        # Get packet data
        start = packet_num * packet_size
        end = min(start + packet_size, total_bytes)
        packet_data = firmware_data[start:end]
        
        # Pad to 8 bytes if needed
        if len(packet_data) < 8:
            packet_data = packet_data + b'\x00' * (8 - len(packet_data))
        
        # Build command
        cmd = bytearray([0x41, 0x54])  # AT
        cmd.append(0x0D)  # Command byte (13)
        cmd.extend([(can_id_29bit >> 16) & 0xFF, (can_id_29bit >> 8) & 0xFF])
        cmd.append(can_id_29bit & 0xFF)
        
        # Data: Byte0~1 = current position (little endian), Byte2~7 = data
        cmd.extend(struct.pack('<H', packet_num))  # 2 bytes packet position
        cmd.extend(packet_data[:6])  # 6 bytes of data
        cmd.extend([0x0d, 0x0a])
        
        # Send packet
        send_l91_command(ser, bytes(cmd))
        
        # Progress indicator
        if packet_num % 100 == 0 or packet_num == packet_count - 1:
            progress = (packet_num + 1) / packet_count * 100
            print(f"  Progress: {packet_num + 1}/{packet_count} ({progress:.1f}%)")
        
        # Small delay between packets
        time.sleep(0.05)
    
    print(f"\n  ✓ All data sent!")
    return True

def update_motor_firmware(ser, target_can_id, firmware_file):
    """
    Complete firmware update process for one motor
    """
    print("="*70)
    print(f"  Firmware Update: Motor CAN ID {target_can_id}")
    print("="*70)
    
    # Read firmware file
    try:
        with open(firmware_file, 'rb') as f:
            firmware_data = f.read()
        print(f"\n✓ Firmware file loaded: {len(firmware_data)} bytes")
    except Exception as e:
        print(f"\n✗ Error reading firmware file: {e}")
        return False
    
    # Step 1: Get device ID
    mcu_id = get_device_id(ser, target_can_id)
    if not mcu_id:
        print("\n✗ Failed to get device ID")
        return False
    
    time.sleep(0.5)
    
    # Step 2: Start upgrade
    if not send_upgrade_start(ser, target_can_id, mcu_id):
        print("\n✗ Failed to start upgrade")
        return False
    
    time.sleep(0.5)
    
    # Step 3: Send upgrade info
    packet_size = 6  # 6 bytes per packet (as per protocol)
    packet_count = (len(firmware_data) + packet_size - 1) // packet_size
    
    if not send_upgrade_info(ser, target_can_id, len(firmware_data), packet_count):
        print("\n✗ Failed to send upgrade info")
        return False
    
    time.sleep(0.5)
    
    # Step 4: Send firmware data
    print("\n⚠️  DO NOT INTERRUPT! Motor will be bricked if interrupted!")
    time.sleep(2)
    
    if not send_upgrade_data(ser, target_can_id, firmware_data, packet_size):
        print("\n✗ Failed to send firmware data")
        return False
    
    print("\n" + "="*70)
    print("✓ FIRMWARE UPDATE COMPLETE!")
    print("="*70)
    print("\nMotor will restart automatically.")
    print("Wait 10 seconds for motor to reboot...")
    time.sleep(10)
    
    return True

def main():
    if len(sys.argv) < 4:
        print("="*70)
        print("  RobStride Motor OTA Firmware Updater")
        print("="*70)
        print("\nUsage: python3 ota_firmware_updater.py <PORT> <BAUD> <FIRMWARE_FILE> [CAN_ID]")
        print("\nExamples:")
        print("  python3 ota_firmware_updater.py /dev/ttyUSB0 921600 RS00_firmware.bin 8")
        print("  python3 ota_firmware_updater.py /dev/ttyUSB0 921600 RS00_firmware.hex")
        print("\nIf CAN_ID not specified, will attempt to update all found motors.")
        print("\n⚠️  WARNING:")
        print("  - Ensure stable power supply")
        print("  - Don't interrupt the process")
        print("  - Test on ONE motor first")
        print("  - Can brick motor if interrupted!")
        sys.exit(1)
    
    port = sys.argv[1]
    baud = int(sys.argv[2])
    firmware_file = sys.argv[3]
    target_can_id = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    print("="*70)
    print("  RobStride Motor OTA Firmware Updater")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}")
    print(f"Firmware: {firmware_file}")
    if target_can_id:
        print(f"Target Motor: CAN ID {target_can_id}")
    else:
        print(f"Target: ALL motors")
    
    print("\n" + "="*70)
    print("⚠️  CRITICAL WARNINGS")
    print("="*70)
    print("1. Ensure STABLE POWER to all motors")
    print("2. Do NOT interrupt the update process")
    print("3. Motor will be BRICKED if power is lost")
    print("4. Test on ONE motor first")
    print("5. Have a backup plan")
    print("\n" + "="*70)
    
    confirm = input("\nType 'YES' to continue (anything else to cancel): ")
    if confirm != 'YES':
        print("\nCancelled by user")
        sys.exit(0)
    
    try:
        # Open serial port
        print(f"\nOpening serial port {port}...")
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("✓ Serial port opened\n")
        
        # Send detection command
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        ser.write(detect_cmd)
        ser.flush()
        time.sleep(0.5)
        
        if target_can_id:
            # Update single motor
            success = update_motor_firmware(ser, target_can_id, firmware_file)
            if success:
                print("\n✓ Firmware update successful!")
            else:
                print("\n✗ Firmware update failed!")
        else:
            # Update all motors
            motor_ids = [8, 16, 21, 31, 64, 72]  # Known motor IDs
            print(f"\nWill update {len(motor_ids)} motors: {motor_ids}")
            print("\n⚠️  This will take a long time!")
            
            confirm2 = input("\nType 'YES' to update all motors: ")
            if confirm2 != 'YES':
                print("\nCancelled")
                sys.exit(0)
            
            for motor_id in motor_ids:
                print(f"\n\n{'#'*70}")
                print(f"# Updating Motor {motor_id}")
                print(f"{'#'*70}\n")
                
                success = update_motor_firmware(ser, motor_id, firmware_file)
                if not success:
                    print(f"\n✗ Failed to update motor {motor_id}")
                    break
                
                print(f"\n✓ Motor {motor_id} updated successfully!")
                time.sleep(5)
        
        ser.close()
        print("\n[COMPLETE]")
        
    except FileNotFoundError:
        print(f"\n✗ Firmware file not found: {firmware_file}")
        print("\nPlease download firmware from:")
        print("https://github.com/RobStride/Product_Information/releases")
        sys.exit(1)
    except serial.SerialException as e:
        print(f"\n✗ Serial port error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERRUPTED BY USER!")
        print("Motor may be in inconsistent state!")
        print("Power cycle motor and try again.")
        if 'ser' in locals():
            ser.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        if 'ser' in locals():
            ser.close()
        sys.exit(1)

if __name__ == '__main__':
    main()

