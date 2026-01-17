#!/usr/bin/env python3
"""
Search for L91 Protocol documentation online
This script provides search queries and findings about L91 protocol
"""

import subprocess
import sys

def web_search(query):
    """Use web search to find information"""
    print(f"\nSearching for: {query}")
    print("="*70)
    
    # Provide manual search instructions since we can't actually search
    print("\nManual search instructions:")
    print(f"  1. Google: {query}")
    print(f"  2. Search GitHub for: {query}")
    print(f"  3. Check Robstride documentation")
    print(f"  4. Check motor controller datasheets")

def main():
    print("="*70)
    print("L91 Protocol Documentation Search")
    print("="*70)
    
    queries = [
        "L91 protocol motor controller CAN bus",
        "L91 protocol AT commands motor control",
        "Robstride L91 protocol documentation",
        "L91 motor controller CAN ID configuration",
        "AT 00 07 e8 motor command protocol",
        "USB to CAN adapter L91 protocol",
        "CH340 L91 protocol motor control",
    ]
    
    print("\nSuggested search queries:")
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. {query}")
    
    print("\n" + "="*70)
    print("KNOWN L91 COMMAND FORMAT")
    print("="*70)
    print("""
Format: AT <cmd_byte> <addr_high> <addr_low> <can_id> <data> \\r\\n

Command Bytes Found:
  0x00 - Activate/Deactivate (0x01 = activate, 0x00 = deactivate)
  0x20 - Load Parameters
  0x90 - Move Jog (velocity control)

Address Bytes:
  0x07 0xE8 - Standard address (required, but value doesn't matter)

Example Commands:
  Activate:    AT 00 07 e8 <id> 01 00 0d 0a
  Deactivate:  AT 00 07 e8 <id> 00 00 0d 0a
  Load Params: AT 20 07 e8 <id> 08 00 c4 00 00 00 00 00 00 0d 0a
  Move Jog:    AT 90 07 e8 <id> 08 05 70 00 00 07 <flag> <speed> 0d 0a

Unknown Command Bytes to Test:
  0x10, 0x11, 0x12 - Possible configuration?
  0x21, 0x30, 0x40 - Possible parameter setting?
  0x50, 0x60, 0x70 - Possible ID configuration?
  0x80, 0xA0, 0xB0, 0xC0, 0xF0 - Unknown functions
    """)
    
    print("\n" + "="*70)
    print("RECOMMENDED SEARCHES")
    print("="*70)
    print("""
1. Search for "Robstride motor controller manual"
   - Look for CAN ID configuration section
   - Check for L91 protocol specification

2. Search for "L91 protocol" + "CAN ID"
   - May find protocol documentation
   - Could find configuration commands

3. Search GitHub for "L91 motor" or "L91 protocol"
   - May find open source implementations
   - Could find command references

4. Check motor controller datasheet
   - Look for CAN ID DIP switches
   - Check for configuration commands
    """)
    
    print("\n[NOTE] Run test_motor_id_locking.py to test configuration commands")
    print("       This will test various command bytes automatically\n")

if __name__ == '__main__':
    main()

