#!/usr/bin/env python3
"""
Diagnose CAN connection issues
"""
import can
import os
import subprocess
import time

def check_can_interfaces():
    """Check CAN interface status"""
    print("=" * 70)
    print("CAN INTERFACE DIAGNOSTICS")
    print("=" * 70)
    
    for iface in ['can0', 'can1']:
        print(f"\n{iface}:")
        print("-" * 70)
        
        # Check if interface exists
        if not os.path.exists(f'/sys/class/net/{iface}'):
            print(f"  ❌ Interface does not exist")
            continue
        
        # Get interface details
        try:
            result = subprocess.run(['ip', '-details', 'link', 'show', iface], 
                                  capture_output=True, text=True)
            print(f"  Status: {result.stdout.strip()}")
        except Exception as e:
            print(f"  ❌ Error getting status: {e}")
        
        # Check for errors
        try:
            result = subprocess.run(['ip', '-s', 'link', 'show', iface],
                                  capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'RX' in line or 'TX' in line or 'errors' in line:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"  ⚠️  Could not get statistics: {e}")

def test_single_message(interface):
    """Test sending a single CAN message"""
    print(f"\n\n{'=' * 70}")
    print(f"TESTING SINGLE MESSAGE ON {interface}")
    print("=" * 70)
    
    try:
        print(f"\n1. Creating bus connection...")
        bus = can.interface.Bus(channel=interface, interface='socketcan')
        print(f"   ✓ Connected")
        
        print(f"\n2. Sending test message (ID=0x01, data=[0x00]*8)...")
        msg = can.Message(
            arbitration_id=0x01,
            data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            is_extended_id=False
        )
        
        try:
            bus.send(msg, timeout=1.0)
            print(f"   ✓ Message sent successfully")
        except can.CanError as e:
            print(f"   ❌ Send failed: {e}")
            print(f"   Error code: {e.error_code if hasattr(e, 'error_code') else 'N/A'}")
            
            # Check bus state
            print(f"\n3. Checking bus state...")
            try:
                result = subprocess.run(['ip', '-details', 'link', 'show', interface],
                                      capture_output=True, text=True)
                if 'ERROR' in result.stdout or 'BUS-OFF' in result.stdout:
                    print(f"   ⚠️  Bus is in error state!")
                    print(f"   {result.stdout}")
                    print(f"\n   Attempting to restart...")
                    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'])
                    time.sleep(0.5)
                    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'])
                    print(f"   ✓ Interface restarted")
            except Exception as e2:
                print(f"   ❌ Could not check/restart: {e2}")
        
        print(f"\n4. Listening for responses (2 seconds)...")
        start = time.time()
        msg_count = 0
        while time.time() - start < 2.0:
            msg = bus.recv(timeout=0.5)
            if msg:
                msg_count += 1
                print(f"   📨 Received: ID=0x{msg.arbitration_id:03X}, Data={msg.data.hex()}")
        
        if msg_count == 0:
            print(f"   ⚠️  No messages received")
        
        bus.shutdown()
        print(f"\n5. Bus closed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def check_physical_connection():
    """Check for physical CAN connection issues"""
    print(f"\n\n{'=' * 70}")
    print("PHYSICAL CONNECTION CHECKLIST")
    print("=" * 70)
    
    print("""
For Motor 2 to work on CAN bus, you need:

1. ✓ Power
   - Motor 2 must be powered (12-48V depending on model)
   - Check power LED on motor

2. ✓ CAN Wiring
   - CAN-H (usually white or yellow)
   - CAN-L (usually blue or green)  
   - GND (ground reference)
   
3. ✓ CAN Termination
   - 120Ω resistor at EACH end of CAN bus
   - Without termination, you get "No buffer space" errors
   
4. ✓ Correct Interface
   - Motor 2 must be connected to can0 OR can1
   - Not both
   
5. ✓ Motor Configuration
   - Motor must be configured for CAN communication
   - Motor ID must be set (expected: 16-20 for Motor 2)
   
Current Status:
""")
    
    # Check which motors might be connected
    print("  Checking for USB-CAN adapters...")
    try:
        result = subprocess.run(['ls', '-la', '/dev/ttyUSB*'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Found: {result.stdout.strip()}")
            print(f"    (Motor might be connected via USB adapter, not direct CAN)")
        else:
            print(f"  ⚠️  No USB-CAN adapters found")
    except Exception as e:
        print(f"  ⚠️  Could not check USB devices")

def main():
    print("\n🔧 CAN Connection Diagnostics\n")
    
    # Step 1: Check interfaces
    check_can_interfaces()
    
    # Step 2: Test can0
    test_single_message('can0')
    
    # Step 3: Test can1
    test_single_message('can1')
    
    # Step 4: Physical connection advice
    check_physical_connection()
    
    print(f"\n\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    print("""
If you're getting "No buffer space available" errors:

1. Check CAN termination (120Ω resistors)
2. Verify Motor 2 is powered ON
3. Confirm Motor 2 is physically connected to can0 or can1
4. Check if Motor 2 is actually connected via USB (/dev/ttyUSB0)
   instead of direct CAN

To test via USB instead:
  python3 test_motor2_simple.py /dev/ttyUSB0 921600
""")

if __name__ == "__main__":
    main()

