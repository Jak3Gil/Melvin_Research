#!/usr/bin/env python3
"""
Analyze Motor Incident - Understand What Happened
This script analyzes the command sequence that caused motors to spin out of control
"""
import struct

def build_move_jog_cmd_analysis(can_id, speed=0.0, flag=1):
    """Analyze the move jog command format"""
    # Speed calculation: 0.1 RPM = 1 count
    speed_val = int(speed * 10) & 0xFFFF
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, flag])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def analyze_incident():
    """Analyze what happened during the motor incident"""
    print("="*70)
    print("  MOTOR INCIDENT ANALYSIS")
    print("="*70)
    print()
    print("What happened:")
    print("1. Script automatically tested motors with 'pulse' action")
    print("2. Sequence sent to each motor:")
    print()
    
    motor_id = 40  # Example motor ID
    print(f"Motor ID: {motor_id}")
    print()
    
    # Step 1: Enable
    enable_cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
    print("Step 1: ENABLE MOTOR")
    print(f"  Command: {enable_cmd.hex(' ')}")
    print(f"  Meaning: Activate motor (enable power)")
    print()
    
    # Step 2: Move forward (10.0 RPM)
    move_forward = build_move_jog_cmd_analysis(motor_id, speed=10.0, flag=1)
    print("Step 2: MOVE FORWARD (10.0 RPM)")
    print(f"  Command: {move_forward.hex(' ')}")
    print(f"  Speed value: {int(10.0 * 10)} (0x{int(10.0 * 10):04X})")
    print(f"  Meaning: Start moving forward at 10.0 RPM")
    print()
    
    # Step 3: Move backward (-10.0 RPM)
    move_backward = build_move_jog_cmd_analysis(motor_id, speed=-10.0, flag=1)
    print("Step 3: MOVE BACKWARD (-10.0 RPM)")
    print(f"  Command: {move_backward.hex(' ')}")
    speed_val_neg = int(-10.0 * 10) & 0xFFFF  # This wraps to large positive!
    print(f"  Speed value: {speed_val_neg} (0x{speed_val_neg:04X}) - PROBLEM!")
    print(f"  !!! NEGATIVE SPEED WRAPS TO POSITIVE: {speed_val_neg} (should be negative!)")
    print(f"  Meaning: Tried to move backward, but calculation may be wrong")
    print()
    
    # Step 4: Stop (speed = 0.0)
    stop_cmd = build_move_jog_cmd_analysis(motor_id, speed=0.0, flag=1)
    print("Step 4: STOP (speed = 0.0)")
    print(f"  Command: {stop_cmd.hex(' ')}")
    print(f"  Speed value: {int(0.0 * 10)} (0x{int(0.0 * 10):04X})")
    print(f"  !!! POTENTIAL ISSUE: Speed = 0 may not stop motor in jog mode!")
    print(f"  Meaning: Attempted to stop, but motor may continue")
    print()
    
    # Step 5: Disable
    disable_cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x00, 0x00, 0x0d, 0x0a])
    print("Step 5: DISABLE MOTOR")
    print(f"  Command: {disable_cmd.hex(' ')}")
    print(f"  Meaning: Deactivate motor (disable power)")
    print()
    
    print("="*70)
    print("  ROOT CAUSE ANALYSIS")
    print("="*70)
    print()
    print("🔴 PROBLEM 1: Speed calculation for negative values")
    print("   - Negative speed (-10.0 RPM) gets converted incorrectly")
    print("   - Python: int(-10.0 * 10) & 0xFFFF = 65436 (0xFF9C)")
    print("   - This is a LARGE positive value, not negative!")
    print("   - Motor may interpret this as very high speed forward")
    print()
    print("🔴 PROBLEM 2: Speed = 0 may not stop motor")
    print("   - Jog mode may require specific stop command")
    print("   - Speed = 0 might mean 'keep current speed' in some protocols")
    print("   - Motor may continue with last commanded speed")
    print()
    print("🔴 PROBLEM 3: Timing issues")
    print("   - 0.2 second timeout may be too short")
    print("   - Motor may not have processed stop command before next command")
    print("   - Commands may have been sent too quickly")
    print()
    print("🔴 PROBLEM 4: No proper stop command")
    print("   - L91 protocol may require explicit stop command (not speed=0)")
    print("   - Or need to disable motor BEFORE stopping")
    print()
    print("="*70)
    print("  WHY MOTORS SPUN OUT OF CONTROL")
    print("="*70)
    print()
    print("Most likely sequence:")
    print("1. ✅ Motor enabled successfully")
    print("2. ✅ Forward command sent (10.0 RPM)")
    print("3. ❌ Backward command sent, but speed calculation WRONG")
    print("   - Negative speed wrapped to large positive value")
    print("   - Motor received high-speed forward command instead")
    print("4. ❌ Stop command (speed=0) didn't work")
    print("   - Motor continued at high speed")
    print("5. ❌ Disable command may not have executed")
    print("   - Or motor didn't respond to disable while moving")
    print()
    print("Result: Motor spinning at high speed, not responding to stop/disable")
    print()
    
    print("="*70)
    print("  SOLUTION")
    print("="*70)
    print()
    print("✅ FIXED: Removed automatic movement tests")
    print("✅ FIXED: Script now only tests communication (enable/disable)")
    print()
    print("For proper motor control:")
    print("1. Always disable motor BEFORE sending movement commands")
    print("2. Use correct speed calculation for negative values")
    print("3. Send explicit stop command (if protocol supports it)")
    print("4. Wait for motor to respond before sending next command")
    print("5. Test with very low speeds first (< 1 RPM)")
    print()

if __name__ == '__main__':
    analyze_incident()

