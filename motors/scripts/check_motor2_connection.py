#!/usr/bin/env python3
"""
Check Motor 2 connection and provide diagnostic information
"""
import serial
import time
import sys

def check_usb_adapter(port, baudrate):
    """Check if USB-to-CAN adapter is responding"""
    print("=" * 70)
    print("  USB-to-CAN Adapter Check")
    print("=" * 70)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print(f"\n✓ Port {port} opened successfully")
        print(f"  Baudrate: {baudrate}")
        print()
        
        # Test 1: AT command
        print("Test 1: Sending AT+AT command...")
        ser.reset_input_buffer()
        ser.write(b'AT+AT\r\n')
        time.sleep(0.3)
        response = ser.read(100)
        
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"  ✅ Adapter responded: '{decoded}'")
            if 'OK' in decoded:
                print(f"     Adapter is working correctly!")
        else:
            print(f"  ❌ No response from adapter")
            print(f"     Adapter may not be L91 compatible")
        print()
        
        # Test 2: Listen for any traffic
        print("Test 2: Listening for CAN traffic (5 seconds)...")
        print("  (If motor is powered and transmitting, we should see data)")
        ser.reset_input_buffer()
        
        start_time = time.time()
        data_received = False
        
        while time.time() - start_time < 5.0:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    data_received = True
                    print(f"  📨 Data received: {data.hex()}")
                    print(f"     ASCII: {data.decode('utf-8', errors='ignore')}")
            time.sleep(0.1)
        
        if not data_received:
            print(f"  ⚠️  No spontaneous CAN traffic detected")
            print(f"     This is normal if motor is not actively transmitting")
        print()
        
        # Test 3: Send broadcast message
        print("Test 3: Sending broadcast enable command...")
        print("  (This should enable ALL motors on the bus)")
        
        # Broadcast to ID 0 (if supported)
        packet = bytearray([0xAA, 0x55, 0x01, 0x00])  # ID 0
        packet.extend([0x00, 0x00, 0x00, 0x00])  # Motor ID field
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # Enable
        checksum = sum(packet[2:]) & 0xFF
        packet.append(checksum)
        
        ser.reset_input_buffer()
        ser.write(packet)
        print(f"  Sent: {packet.hex()}")
        time.sleep(0.5)
        
        response = ser.read(100)
        if response:
            print(f"  ✅ Response received: {response.hex()}")
            print(f"     A motor is connected and responding!")
        else:
            print(f"  ⚠️  No response to broadcast")
        print()
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"\n❌ Cannot open port: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🔧 Motor 2 Connection Diagnostic\n")
    
    port = '/dev/ttyUSB1'
    baudrate = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    
    print(f"Configuration:")
    print(f"  Port: {port}")
    print(f"  Baudrate: {baudrate}\n")
    
    # Check adapter
    adapter_ok = check_usb_adapter(port, baudrate)
    
    # Provide troubleshooting guide
    print("\n" + "=" * 70)
    print("  TROUBLESHOOTING GUIDE")
    print("=" * 70)
    print("""
If Motor 2 is not responding, check the following:

1. POWER
   ✓ Is Motor 2 powered on? (12-48V depending on model)
   ✓ Check for LED indicator on motor
   ✓ Measure voltage at motor power terminals

2. CAN WIRING
   ✓ CAN-H connected (usually white/yellow wire)
   ✓ CAN-L connected (usually blue/green wire)
   ✓ Ground (GND) connected
   ✓ Wires not reversed
   ✓ No loose connections

3. CAN TERMINATION
   ✓ 120Ω resistor at each end of CAN bus
   ✓ For single motor test: one 120Ω between CAN-H and CAN-L

4. MOTOR CONFIGURATION
   ✓ Motor must be configured for CAN communication
   ✓ Motor ID must be set (not at default/unconfigured state)
   ✓ Motor firmware must be compatible with L91 protocol

5. USB ADAPTER
   ✓ Adapter is connected to Jetson
   ✓ Adapter is powered (if external power needed)
   ✓ Adapter LED indicators (if any) showing activity

6. PHYSICAL SETUP
   ✓ Only Motor 2 is connected (no other motors)
   ✓ Motor is the correct one (labeled as Motor 2)
   ✓ CAN bus length is reasonable (< 40m for 1Mbps)

NEXT STEPS:

If adapter responds but motor doesn't:
  → Motor is likely not powered or not configured

If adapter doesn't respond:
  → Try different baudrate: python3 check_motor2_connection.py /dev/ttyUSB1 115200
  → Check USB connection: ls -la /dev/ttyUSB*
  → Try different port: python3 check_motor2_connection.py /dev/ttyUSB0 921600

If you see "OK" from adapter but no motor response:
  → Motor 2 is NOT powered or NOT connected to CAN bus
  → Check power supply to motor
  → Verify CAN wiring with multimeter
  → Check if motor needs to be configured first
""")
    
    print("\n" + "=" * 70)
    print("  QUICK TESTS")
    print("=" * 70)
    print(f"""
To test with different settings:

Different baudrate:
  python3 check_motor2_connection.py {port} 115200

Different port:
  python3 check_motor2_connection.py /dev/ttyUSB0 921600

Scan for motors (if motor is powered):
  python3 find_motor2_l91.py {port} {baudrate}

Test specific motor ID (if you know it):
  python3 quick_motor_test.py {port} {baudrate} <MOTOR_ID>
""")

if __name__ == "__main__":
    main()

