#!/usr/bin/env python3
"""
Motor Groups Summary - Quick Reference
Shows the 4 identified motor groups and their CAN ID ranges
"""

def print_motor_groups():
    """Display motor groups in a clear format"""
    
    print("="*70)
    print("MOTOR GROUPS SUMMARY - 6 Physical Motors Identified")
    print("="*70)
    print()
    
    motors = [
        {
            'name': 'Motor 1',
            'can_ids': list(range(8, 11)),
            'recommended_id': 8,
            'response_sig': '41 54 00 00 0f f4 08 36 45 3b 4e 20 71 30 18 0d 0a'
        },
        {
            'name': 'Motor 2',
            'can_ids': [20],
            'recommended_id': 20,
            'response_sig': '41 54 10 00 17 ec 08 00 c4 56 00 03 01 0b 07 0d 0a'
        },
        {
            'name': 'Motor 3',
            'can_ids': [31],
            'recommended_id': 31,
            'response_sig': '41 54 00 00 1f f4 08 40 64 3b 4e 20 71 30 18 0d 0a'
        },
        {
            'name': 'Motor 4',
            'can_ids': list(range(32, 40)),
            'recommended_id': 32,
            'response_sig': '41 54 00 00 27 f4 08 3b 44 30 02 14 33 b2 17 0d 0a'
        },
        {
            'name': 'Motor 5',
            'can_ids': list(range(64, 72)),
            'recommended_id': 64,
            'response_sig': '41 54 00 00 47 f4 08 43 3c 30 02 14 33 b2 18 0d 0a'
        },
        {
            'name': 'Motor 6',
            'can_ids': list(range(72, 80)),
            'recommended_id': 72,
            'response_sig': '41 54 00 00 4f f4 08 c9 42 30 20 9c 23 37 0d 0d 0a'
        }
    ]
    
    for i, motor in enumerate(motors, 1):
        print(f"+{'-'*66}+")
        print(f"| {motor['name']:<64} |")
        print(f"+{'-'*66}+")
        print(f"| CAN IDs: {motor['can_ids'][0]}-{motor['can_ids'][-1]} ({len(motor['can_ids'])} IDs)".ljust(67) + "|")
        print(f"| Recommended ID: {motor['recommended_id']:<48} |")
        print(f"| Response Signature:".ljust(67) + "|")
        print(f"|   {motor['response_sig'][:50]:<50} |")
        if len(motor['response_sig']) > 50:
            print(f"|   {motor['response_sig'][50:]:<50} |")
        print(f"+{'-'*66}+")
        print()
    
    print("="*70)
    print("USAGE RECOMMENDATIONS")
    print("="*70)
    print()
    print("To control each motor individually, use the recommended CAN ID:")
    print()
    for motor in motors:
        print(f"  {motor['name']}: Use CAN ID {motor['recommended_id']}")
    print()
    print("Example Python code:")
    print()
    print("  # Control Motor 1")
    print("  activate_motor(8)")
    print("  move_motor(8, speed=0.5, direction=1)")
    print()
    print("  # Control Motor 2")
    print("  activate_motor(16)")
    print("  move_motor(16, speed=0.5, direction=1)")
    print()
    print("="*70)
    print()
    print("STATUS: 6 motors found, 9 motors still missing (if 15 expected)")
    print("SCAN: Complete (IDs 1-255 scanned)")
    print("NEXT: Verify physical motor count and connections")
    print()

if __name__ == '__main__':
    print_motor_groups()

