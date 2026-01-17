#!/usr/bin/env python3
"""
Analyze Captured Motor Studio Commands
Parses captured commands and extracts CANopen protocol format
"""
import re
import csv
from collections import defaultdict

def parse_hex_string(hex_str):
    """Parse hex string to bytes"""
    # Remove spaces, colons, 0x prefixes
    hex_str = hex_str.replace(' ', '').replace(':', '').replace('0x', '')
    
    try:
        return bytes.fromhex(hex_str)
    except:
        return None

def analyze_at_command(cmd_bytes):
    """Analyze AT/L91 format command"""
    if len(cmd_bytes) < 3:
        return None
    
    # Check for AT header
    if cmd_bytes[0] != 0x41 or cmd_bytes[1] != 0x54:
        return None
    
    analysis = {
        'type': 'AT/L91',
        'header': 'AT',
        'command_byte': cmd_bytes[2],
        'raw_bytes': cmd_bytes.hex(' '),
        'length': len(cmd_bytes)
    }
    
    # Parse common formats
    if len(cmd_bytes) >= 10:
        if cmd_bytes[2] == 0x00:
            # Standard format: AT + 0x00 + CAN ID + Data
            analysis['format'] = 'Standard AT'
            analysis['can_id'] = (cmd_bytes[3] << 8) | cmd_bytes[4]
            analysis['data'] = cmd_bytes[5:].hex(' ')
            
        elif cmd_bytes[2] == 0x20:
            # Parameter write format
            analysis['format'] = 'Parameter Write'
            analysis['can_id'] = (cmd_bytes[3] << 8) | cmd_bytes[4]
            analysis['data'] = cmd_bytes[5:].hex(' ')
            
        elif cmd_bytes[2] == 0x01:
            # CAN TX format
            analysis['format'] = 'Raw CAN TX'
            analysis['can_id'] = (cmd_bytes[3] << 8) | cmd_bytes[4]
            analysis['data_length'] = cmd_bytes[5]
            analysis['data'] = cmd_bytes[6:].hex(' ')
    
    return analysis

def analyze_canopen_message(can_id, data_bytes):
    """Analyze CANopen message"""
    analysis = {
        'type': 'CANopen',
        'can_id': can_id,
        'data': data_bytes.hex(' ') if isinstance(data_bytes, bytes) else data_bytes
    }
    
    # NMT messages (0x000)
    if can_id == 0x000:
        if len(data_bytes) >= 2:
            analysis['message_type'] = 'NMT'
            cmd = data_bytes[0]
            node_id = data_bytes[1]
            
            nmt_commands = {
                0x01: 'Start Remote Node',
                0x02: 'Stop Remote Node',
                0x80: 'Pre-operational',
                0x81: 'Reset Node',
                0x82: 'Reset Communication'
            }
            
            analysis['nmt_command'] = nmt_commands.get(cmd, f'Unknown ({cmd:02X})')
            analysis['node_id'] = node_id
    
    # SDO messages (0x600-0x67F, 0x580-0x5FF)
    elif 0x600 <= can_id <= 0x67F:
        node_id = can_id - 0x600
        analysis['message_type'] = 'SDO Client-to-Server'
        analysis['node_id'] = node_id
        
        if len(data_bytes) >= 1:
            cmd_byte = data_bytes[0]
            
            if cmd_byte == 0x40:
                analysis['sdo_type'] = 'Expedited Read (4 bytes)'
                if len(data_bytes) >= 4:
                    index = (data_bytes[2] << 8) | data_bytes[1]
                    subindex = data_bytes[3]
                    analysis['object_index'] = f'0x{index:04X}'
                    analysis['subindex'] = f'0x{subindex:02X}'
            
            elif cmd_byte == 0x23:
                analysis['sdo_type'] = 'Expedited Write (4 bytes)'
                if len(data_bytes) >= 8:
                    index = (data_bytes[2] << 8) | data_bytes[1]
                    subindex = data_bytes[3]
                    value = int.from_bytes(data_bytes[4:8], 'little')
                    analysis['object_index'] = f'0x{index:04X}'
                    analysis['subindex'] = f'0x{subindex:02X}'
                    analysis['value'] = f'0x{value:08X} ({value})'
    
    elif 0x580 <= can_id <= 0x5FF:
        node_id = can_id - 0x580
        analysis['message_type'] = 'SDO Server-to-Client'
        analysis['node_id'] = node_id
    
    # PDO messages (0x180-0x57F)
    elif 0x180 <= can_id <= 0x57F:
        analysis['message_type'] = 'PDO'
        # TPDO1: 0x180-0x1FF
        # RPDO1: 0x200-0x27F
        # etc.
        base = (can_id // 0x80) * 0x80
        node_id = can_id - base
        analysis['pdo_type'] = f'TPDO{(can_id // 0x80) - 1}' if base < 0x400 else f'RPDO{(can_id // 0x80) - 5}'
        analysis['node_id'] = node_id
    
    # Heartbeat (0x700-0x77F)
    elif 0x700 <= can_id <= 0x77F:
        node_id = can_id - 0x700
        analysis['message_type'] = 'Heartbeat'
        analysis['node_id'] = node_id
        if len(data_bytes) >= 1:
            state = data_bytes[0]
            states = {
                0x00: 'Initialization',
                0x04: 'Stopped',
                0x05: 'Operational',
                0x7F: 'Pre-operational'
            }
            analysis['state'] = states.get(state, f'Unknown ({state:02X})')
    
    return analysis

def parse_csv_capture(filename):
    """Parse CSV format capture file"""
    commands = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            first_line = f.readline()
            f.seek(0)
            
            if ',' in first_line:
                reader = csv.DictReader(f)
            elif '\t' in first_line:
                reader = csv.DictReader(f, delimiter='\t')
            else:
                # Try to parse as simple format
                for line in f:
                    if line.strip():
                        # Look for hex data
                        hex_match = re.search(r'([0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2})+|[0-9A-Fa-f]{4,})', line)
                        if hex_match:
                            hex_str = hex_match.group(1)
                            commands.append({
                                'time': '',
                                'direction': 'TX' if 'TX' in line or 'Send' in line else 'RX',
                                'data': hex_str
                            })
                return commands
            
            for row in reader:
                # Try to find hex data column
                hex_data = None
                for key in row:
                    if 'hex' in key.lower() or 'data' in key.lower():
                        hex_data = row[key]
                        break
                
                if not hex_data:
                    # Look for hex pattern in any column
                    for key, value in row.items():
                        if re.match(r'^[0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2})+$', value or ''):
                            hex_data = value
                            break
                
                if hex_data:
                    commands.append({
                        'time': row.get('Time', row.get('time', '')),
                        'direction': row.get('Direction', row.get('direction', row.get('Type', ''))),
                        'data': hex_data
                    })
    
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return []
    
    return commands

def parse_txt_capture(filename):
    """Parse text format capture file"""
    commands = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # Look for hex patterns
                hex_match = re.search(r'([0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2})+)', line)
                if hex_match:
                    direction = 'TX' if 'TX' in line or 'Send' in line or '→' in line else 'RX'
                    commands.append({
                        'time': '',
                        'direction': direction,
                        'data': hex_match.group(1)
                    })
    except Exception as e:
        print(f"Error parsing TXT: {e}")
        return []
    
    return commands

def analyze_commands(commands):
    """Analyze captured commands and extract patterns"""
    
    print("="*70)
    print("  COMMAND ANALYSIS")
    print("="*70)
    print()
    
    # Group by direction
    tx_commands = [c for c in commands if 'TX' in c.get('direction', '').upper() or 'SEND' in c.get('direction', '').upper()]
    rx_commands = [c for c in commands if 'RX' in c.get('direction', '').upper() or 'RECV' in c.get('direction', '').upper()]
    
    print(f"Total commands: {len(commands)}")
    print(f"  TX (Sent): {len(tx_commands)}")
    print(f"  RX (Received): {len(rx_commands)}")
    print()
    
    # Analyze TX commands (what Motor Studio sends)
    print("="*70)
    print("  ANALYZING TX COMMANDS (Motor Studio → Motors)")
    print("="*70)
    print()
    
    at_formats = defaultdict(int)
    canopen_messages = []
    
    for cmd in tx_commands:
        data_bytes = parse_hex_string(cmd['data'])
        if not data_bytes:
            continue
        
        # Try AT format
        at_analysis = analyze_at_command(data_bytes)
        if at_analysis:
            format_key = f"{at_analysis.get('format', 'Unknown')} (0x{at_analysis['command_byte']:02X})"
            at_formats[format_key] += 1
            
            if at_analysis.get('can_id'):
                can_id = at_analysis['can_id']
                data = data_bytes[5:] if len(data_bytes) > 5 else b''
                canopen_analysis = analyze_canopen_message(can_id, data)
                canopen_messages.append(canopen_analysis)
        
        # Try direct CAN ID extraction
        elif len(data_bytes) >= 5:
            # Might be raw CAN frame
            can_id = (data_bytes[3] << 8) | data_bytes[4] if len(data_bytes) >= 5 else None
            if can_id:
                data = data_bytes[5:] if len(data_bytes) > 5 else b''
                canopen_analysis = analyze_canopen_message(can_id, data)
                if canopen_analysis.get('message_type'):
                    canopen_messages.append(canopen_analysis)
    
    # Print AT format statistics
    print("AT/L91 Command Formats Found:")
    for fmt, count in sorted(at_formats.items(), key=lambda x: -x[1]):
        print(f"  {fmt}: {count} commands")
    print()
    
    # Print CANopen message analysis
    if canopen_messages:
        print("CANopen Messages Detected:")
        print()
        
        message_types = defaultdict(list)
        for msg in canopen_messages:
            msg_type = msg.get('message_type', 'Unknown')
            message_types[msg_type].append(msg)
        
        for msg_type, msgs in message_types.items():
            print(f"{msg_type} ({len(msgs)} messages):")
            for msg in msgs[:5]:  # Show first 5 of each type
                print(f"  CAN ID: 0x{msg['can_id']:03X}", end='')
                if msg.get('node_id') is not None:
                    print(f", Node: {msg['node_id']}", end='')
                if msg.get('sdo_type'):
                    print(f", {msg['sdo_type']}", end='')
                if msg.get('object_index'):
                    print(f", Object: {msg['object_index']}", end='')
                print()
            if len(msgs) > 5:
                print(f"  ... and {len(msgs) - 5} more")
            print()
    
    # Generate Python code
    print("="*70)
    print("  GENERATED PYTHON CODE")
    print("="*70)
    print()
    
    if at_formats:
        print("# Most common command format:")
        most_common = max(at_formats.items(), key=lambda x: x[1])
        print(f"# Format: {most_common[0]}")
        print()
        
        # Generate example based on most common format
        if 'Standard AT' in most_common[0] or '0x00' in most_common[0]:
            print("def send_canopen_via_l91(ser, can_id, data):")
            print("    \"\"\"Send CANopen message via L91 protocol\"\"\"")
            print("    cmd = bytearray([0x41, 0x54, 0x00])  # AT header")
            print("    cmd.append((can_id >> 8) & 0xFF)     # CAN ID high")
            print("    cmd.append(can_id & 0xFF)            # CAN ID low")
            print("    cmd.extend(data)                     # CANopen data")
            print("    cmd.extend([0x0D, 0x0A])            # Terminator")
            print("    ser.write(bytes(cmd))")
            print()
        
        elif 'Raw CAN TX' in most_common[0] or '0x01' in most_common[0]:
            print("def send_canopen_raw(ser, can_id, data):")
            print("    \"\"\"Send raw CAN frame via adapter\"\"\"")
            print("    cmd = bytearray([0x41, 0x54, 0x01])  # AT + Raw CAN")
            print("    cmd.append((can_id >> 8) & 0xFF)")
            print("    cmd.append(can_id & 0xFF)")
            print("    cmd.append(len(data))                # Data length")
            print("    cmd.extend(data)")
            print("    cmd.extend([0x0D, 0x0A])")
            print("    ser.write(bytes(cmd))")
            print()
    
    # Show example commands
    print("Example Commands from Capture:")
    print()
    for i, cmd in enumerate(tx_commands[:10], 1):
        data_bytes = parse_hex_string(cmd['data'])
        if data_bytes:
            print(f"#{i}: {cmd['data']}")
            analysis = analyze_at_command(data_bytes)
            if analysis:
                print(f"   Format: {analysis.get('format', 'Unknown')}")
                if analysis.get('can_id'):
                    print(f"   CAN ID: 0x{analysis['can_id']:03X}")
            print()
    
    print("="*70)

def main():
    import sys
    
    print("="*70)
    print("  MOTOR STUDIO COMMAND ANALYZER")
    print("="*70)
    print()
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter capture file path: ").strip().strip('"')
    
    print(f"\nParsing: {filename}")
    print()
    
    # Try to parse based on extension
    if filename.endswith('.csv'):
        commands = parse_csv_capture(filename)
    else:
        commands = parse_txt_capture(filename)
    
    if not commands:
        print("✗ No commands found in file!")
        print("\nMake sure the file contains hex data in one of these formats:")
        print("  - CSV with hex data column")
        print("  - TXT with hex patterns (e.g., '41 54 00 07 E8')")
        return
    
    print(f"✓ Parsed {len(commands)} commands")
    print()
    
    # Analyze
    analyze_commands(commands)
    
    # Save analysis
    output_file = filename.replace('.csv', '_analysis.txt').replace('.txt', '_analysis.txt')
    print(f"\nDetailed analysis saved to: {output_file}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

