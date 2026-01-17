#!/usr/bin/env python3
"""
Comprehensive Motor 2 Finder
Tests multiple ID ranges and CAN bitrates
"""
import can
import time
import sys

def scan_can_range(bus, start_id, end_id, interface_name):
    """Scan a range of CAN IDs"""
    print(f"\nScanning IDs {start_id}-{end_id} on {interface_name}...")
    found = []
    
    for motor_id in range(start_id, end_id + 1):
        # Try enable command (MIT protocol)
        msg = can.Message(
            arbitration_id=motor_id,
            data=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC],
            is_extended_id=False
        )
        bus.send(msg)
        
        # Check for response
        response = bus.recv(timeout=0.1)
        if response:
            print(f"  ✅ ID {motor_id} (0x{motor_id:02X}) - Response: {response.data.hex()}")
            found.append(motor_id)
            
            # Disable it
            msg = can.Message(
                arbitration_id=motor_id,
                data=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD],
                is_extended_id=False
            )
            bus.send(msg)
            time.sleep(0.05)
        
        time.sleep(0.05)
    
    return found

def listen_for_traffic(interface, duration=5):
    """Listen for any CAN traffic"""
    print(f"\n======================================================================")
    print(f"  Listening for CAN traffic on {interface} ({duration}s)")
    print(f"======================================================================\n")
    
    try:
        bus = can.interface.Bus(channel=interface, interface='socketcan')
        print(f"Listening... (press Ctrl+C to stop early)\n")
        
        start_time = time.time()
        message_count = 0
        unique_ids = set()
        
        while time.time() - start_time < duration:
            msg = bus.recv(timeout=0.5)
            if msg:
                message_count += 1
                unique_ids.add(msg.arbitration_id)
                print(f"  [{message_count}] ID: 0x{msg.arbitration_id:03X} ({msg.arbitration_id:3d}) | Data: {msg.data.hex()}")
        
        bus.shutdown()
        
        print(f"\n📊 Summary:")
        print(f"   Total messages: {message_count}")
        print(f"   Unique IDs: {len(unique_ids)}")
        if unique_ids:
            print(f"   IDs seen: {sorted(unique_ids)}")
        
        return list(unique_ids)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user")
        bus.shutdown()
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def comprehensive_scan(interface):
    """Comprehensive scan of all possible motor IDs"""
    print(f"\n======================================================================")
    print(f"  Comprehensive Motor Scan on {interface}")
    print(f"======================================================================")
    
    try:
        bus = can.interface.Bus(channel=interface, interface='socketcan')
        print(f"✓ Connected to {interface}\n")
        
        all_found = []
        
        # Scan different ranges
        ranges = [
            (1, 15, "Motors 1-15 (typical range)"),
            (16, 30, "Motor 2 expected range"),
            (31, 50, "Extended range"),
            (64, 80, "High ID range"),
            (100, 127, "Very high range")
        ]
        
        for start, end, description in ranges:
            print(f"\n--- {description} ---")
            found = scan_can_range(bus, start, end, interface)
            if found:
                print(f"  ✅ Found motors: {found}")
                all_found.extend(found)
            else:
                print(f"  ⚠️  No motors found")
        
        bus.shutdown()
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_specific_motor(motor_id, interface):
    """Test a specific motor with detailed output"""
    print(f"\n======================================================================")
    print(f"  Testing Motor ID {motor_id} on {interface}")
    print(f"======================================================================\n")
    
    try:
        bus = can.interface.Bus(channel=interface, interface='socketcan')
        
        # Test 1: Enable
        print("1. Sending ENABLE command...")
        msg = can.Message(
            arbitration_id=motor_id,
            data=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC],
            is_extended_id=False
        )
        bus.send(msg)
        
        response = bus.recv(timeout=0.5)
        if response:
            print(f"   ✅ Response: {response.data.hex()}")
        else:
            print(f"   ⚠️  No response")
        
        time.sleep(0.2)
        
        # Test 2: Zero position command
        print("\n2. Sending ZERO POSITION command...")
        msg = can.Message(
            arbitration_id=motor_id,
            data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            is_extended_id=False
        )
        bus.send(msg)
        
        response = bus.recv(timeout=0.5)
        if response:
            print(f"   ✅ Response: {response.data.hex()}")
        else:
            print(f"   ⚠️  No response")
        
        time.sleep(0.2)
        
        # Test 3: Disable
        print("\n3. Sending DISABLE command...")
        msg = can.Message(
            arbitration_id=motor_id,
            data=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD],
            is_extended_id=False
        )
        bus.send(msg)
        
        response = bus.recv(timeout=0.5)
        if response:
            print(f"   ✅ Response: {response.data.hex()}")
        else:
            print(f"   ⚠️  No response")
        
        bus.shutdown()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n🔍 Comprehensive Motor 2 Finder\n")
    
    interface = 'can0'
    if len(sys.argv) > 1:
        if sys.argv[1] in ['can0', 'can1']:
            interface = sys.argv[1]
        elif sys.argv[1] == 'listen':
            # Listen mode
            iface = sys.argv[2] if len(sys.argv) > 2 else 'can0'
            duration = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            listen_for_traffic(iface, duration)
            return
        elif sys.argv[1] == 'test':
            # Test specific motor
            motor_id = int(sys.argv[2]) if len(sys.argv) > 2 else 16
            iface = sys.argv[3] if len(sys.argv) > 3 else 'can0'
            test_specific_motor(motor_id, iface)
            return
    
    print(f"Interface: {interface}")
    print(f"\nUsage:")
    print(f"  python3 {sys.argv[0]} [can0|can1]           - Scan for motors")
    print(f"  python3 {sys.argv[0]} listen [can0] [10]    - Listen for traffic")
    print(f"  python3 {sys.argv[0]} test [16] [can0]      - Test specific motor")
    print()
    
    # First, listen for any existing traffic
    print("\n📡 Step 1: Listening for existing CAN traffic...")
    traffic_ids = listen_for_traffic(interface, 3)
    
    if traffic_ids:
        print(f"\n✅ Found active IDs: {traffic_ids}")
        print("\nTesting each active ID...")
        for motor_id in traffic_ids:
            test_specific_motor(motor_id, interface)
    else:
        print("\n⚠️  No existing traffic detected")
        print("\n📡 Step 2: Active scanning...")
        found_motors = comprehensive_scan(interface)
        
        if found_motors:
            print(f"\n\n✅ SUCCESS! Found motors: {found_motors}")
            print(f"\nMotor 2 is likely at ID: {found_motors[0]}")
        else:
            print(f"\n\n❌ No motors found on {interface}")
            print("\nTroubleshooting:")
            print("  1. ✓ CAN interface is UP")
            print("  2. ❓ Is Motor 2 powered on?")
            print("  3. ❓ Is Motor 2 connected to the correct CAN bus?")
            print(f"  4. ❓ Try the other interface: python3 {sys.argv[0]} can1")
            print("  5. ❓ Check CAN bitrate (currently 500000)")
            print("       Try: sudo ip link set can0 down")
            print("            sudo ip link set can0 type can bitrate 1000000")
            print("            sudo ip link set can0 up")

if __name__ == "__main__":
    main()

