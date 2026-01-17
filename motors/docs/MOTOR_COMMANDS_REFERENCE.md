# Motor Commands Reference - From Melvin_november Repository

This document summarizes the motor command protocols found in the [Melvin_november repository](https://github.com/Jak3Gil/Melvin_november).

## Overview

The repository contains code for controlling CAN bus motors, specifically **Robstride O2/O3 motors** and other CAN-based motor controllers. The motors are controlled via USB-to-CAN adapters (CH340-based) using the SLCAN protocol.

## CAN Interface Setup

### USB-to-CAN Setup
- **Interface**: `slcan0` or `can0`
- **Serial Baud Rate**: 921600 baud (for USB serial)
- **CAN Bitrate**: 500kbps (common), 125kbps also used
- **Adapter**: CH340 USB-to-Serial adapters configured with `slcand`

### Setup Script
See `setup_usb_can_motors.sh` for complete setup process:
1. Load CH340 driver
2. Detect USB serial device (`/dev/ttyUSB*`)
3. Install `can-utils` package
4. Start `slcand` to bridge USB serial to CAN
5. Configure CAN interface bitrate
6. Bring interface up

## Motor Command Protocol (Robstride)

### Command Constants

```c
// Motor Control Commands
#define CMD_DISABLE_MOTOR  0xA0   // Disable motor
#define CMD_ENABLE_MOTOR   0xA1   // Enable motor / Position mode
#define CMD_VELOCITY_MODE  0xA2   // Velocity control mode
#define CMD_TORQUE_MODE    0xA3   // Torque control mode
#define CMD_READ_STATE     0x92   // Read motor state
#define CMD_ZERO_POSITION  0x19   // Zero current position

// Generic Motor Commands (from map_can_motors.c)
#define CMD_SET_POSITION  0x01
#define CMD_SET_VELOCITY  0x02
#define CMD_SET_TORQUE    0x03
```

### Motor Parameter Ranges (Robstride)

```c
#define POS_MIN     -12.5f   // Position range (radians)
#define POS_MAX      12.5f
#define VEL_MIN     -65.0f   // Velocity range (rad/s)
#define VEL_MAX      65.0f
#define TORQUE_MIN  -18.0f   // Torque range (Nm)
#define TORQUE_MAX   18.0f
#define KP_MIN        0.0f   // Position gain
#define KP_MAX      500.0f
```

### CAN Frame Structure

```c
struct can_frame {
    uint32_t can_id;        // Motor ID (e.g., 12 = 0x0C, 14 = 0x0E)
    uint8_t  can_dlc;       // Data length (typically 8 bytes)
    uint8_t  data[8];       // Command + parameters
};

// Frame format:
// data[0] = Command byte (0xA1, 0xA2, etc.)
// data[1-2] = Position/Velocity/Torque value (16-bit encoded)
// data[3-4] = Additional parameter (e.g., velocity limit)
// data[5-6] = Additional parameter (e.g., KP gain)
// data[7] = Reserved/flags
```

## Motor Control Functions

### 1. Enable Motor

```c
bool enable_motor(uint8_t motor_id) {
    struct can_frame frame;
    frame.can_id = motor_id;        // e.g., 12, 14
    frame.can_dlc = 8;
    frame.data[0] = CMD_ENABLE_MOTOR;  // 0xA1
    // data[1-7] = 0 (zero padding)
    
    write(can_socket, &frame, sizeof(frame));
    usleep(50000);  // 50ms delay
    return true;
}
```

### 2. Disable Motor

```c
bool disable_motor(uint8_t motor_id) {
    struct can_frame frame;
    frame.can_id = motor_id;
    frame.can_dlc = 8;
    frame.data[0] = CMD_DISABLE_MOTOR;  // 0xA0
    // data[1-7] = 0
    
    write(can_socket, &frame, sizeof(frame));
    usleep(100000);  // 100ms delay
    return true;
}
```

### 3. Set Position (Position Control Mode)

```c
bool set_position(uint8_t motor_id, float position, float velocity, float kp) {
    // Clamp values to valid ranges
    if (position < POS_MIN) position = POS_MIN;
    if (position > POS_MAX) position = POS_MAX;
    if (velocity < 0.0f) velocity = 0.0f;
    if (velocity > VEL_MAX) velocity = VEL_MAX;
    if (kp < KP_MIN) kp = KP_MIN;
    if (kp > KP_MAX) kp = KP_MAX;
    
    struct can_frame frame;
    frame.can_id = motor_id;
    frame.can_dlc = 8;
    frame.data[0] = CMD_POSITION_MODE;  // 0xA1
    
    // Encode position (16-bit, normalized to 0-65535)
    float normalized_pos = (position - POS_MIN) / (POS_MAX - POS_MIN);
    uint16_t pos_encoded = (uint16_t)(normalized_pos * 65535.0f);
    frame.data[1] = (pos_encoded >> 8) & 0xFF;  // High byte
    frame.data[2] = pos_encoded & 0xFF;          // Low byte
    
    // Encode velocity limit
    float normalized_vel = velocity / VEL_MAX;
    uint16_t vel_encoded = (uint16_t)(normalized_vel * 65535.0f);
    frame.data[3] = (vel_encoded >> 8) & 0xFF;
    frame.data[4] = vel_encoded & 0xFF;
    
    // Encode KP gain
    float normalized_kp = (kp - KP_MIN) / (KP_MAX - KP_MIN);
    uint16_t kp_encoded = (uint16_t)(normalized_kp * 65535.0f);
    frame.data[5] = (kp_encoded >> 8) & 0xFF;
    frame.data[6] = kp_encoded & 0xFF;
    
    frame.data[7] = 0;  // Reserved
    
    write(can_socket, &frame, sizeof(frame));
    return true;
}
```

### 4. Set Velocity (Velocity Control Mode)

```c
bool set_velocity(uint8_t motor_id, float velocity) {
    // Similar structure to set_position, but uses CMD_VELOCITY_MODE (0xA2)
    // Velocity range: -65.0 to +65.0 rad/s
    frame.data[0] = CMD_VELOCITY_MODE;  // 0xA2
    // Encode velocity in data[1-2]
    // ...
}
```

### 5. Set Torque (Torque Control Mode)

```c
bool set_torque(uint8_t motor_id, float torque) {
    // Uses CMD_TORQUE_MODE (0xA3)
    // Torque range: -18.0 to +18.0 Nm
    frame.data[0] = CMD_TORQUE_MODE;  // 0xA3
    // Encode torque in data[1-2]
    // ...
}
```

## Value Encoding

### Float to 16-bit CAN Bytes

```c
void float_to_can_bytes(float value, uint8_t* bytes, float min, float max) {
    // Clamp to range
    if (value < min) value = min;
    if (value > max) value = max;
    
    // Normalize to 0-65535 range
    float normalized = (value - min) / (max - min);
    uint16_t encoded = (uint16_t)(normalized * 65535.0f);
    
    bytes[0] = (encoded >> 8) & 0xFF;  // High byte
    bytes[1] = encoded & 0xFF;          // Low byte
}
```

## Example Usage

### Basic Motor Control Sequence

```c
// 1. Initialize CAN interface
init_can();  // Creates socket, binds to can0/slcan0

// 2. Enable motor
enable_motor(12);  // Enable motor with CAN ID 12

// 3. Set position
set_position(12, 0.5f, 10.0f, 50.0f);  
// Position: 0.5 radians, Max velocity: 10 rad/s, KP: 50

// 4. Wait for movement
usleep(1000000);  // 1 second

// 5. Set new position
set_position(12, -0.5f, 10.0f, 50.0f);

// 6. Disable motor when done
disable_motor(12);
```

### Complete Test Program Structure

```c
int main() {
    signal(SIGINT, signal_handler);  // Handle Ctrl+C
    
    if (!init_can()) {
        fprintf(stderr, "Failed to initialize CAN\n");
        return 1;
    }
    
    // Enable motors
    enable_motor(12);
    enable_motor(14);
    
    // Movement sequence
    while (running) {
        set_position(12, 0.5f, 10.0f, 50.0f);
        set_position(14, -0.5f, 10.0f, 50.0f);
        sleep(2);
        
        set_position(12, -0.5f, 10.0f, 50.0f);
        set_position(14, 0.5f, 10.0f, 50.0f);
        sleep(2);
    }
    
    // Cleanup
    disable_motor(12);
    disable_motor(14);
    close(can_socket);
    return 0;
}
```

## Motor IDs (CAN IDs)

- **Motor 12**: CAN ID `0x0C` (12 decimal)
- **Motor 13**: CAN ID `0x0D` (13 decimal)
- **Motor 14**: CAN ID `0x0E` (14 decimal)
- Other motors: Typically CAN IDs 1-14 (0x01-0x0E)

## Key Files in Repository

- `test_motors_12_14.c` - Complete test program for motors 12 & 14
- `test_robstride_motors.c` - Robstride-specific motor tests
- `melvin_motor_runtime.c` - Runtime system that bridges brain EXEC nodes to motors
- `setup_usb_can_motors.sh` - Complete setup script for USB-to-CAN
- `map_can_ids_to_physical_motors.c` - Motor discovery and mapping
- `tools/map_can_motors.c` - CAN motor discovery tool

## Notes

1. **Timing**: Always include delays after enable/disable commands (50-100ms)
2. **Bitrate**: CAN bus should be configured to 500kbps for Robstride motors
3. **USB-to-CAN**: When using USB adapters, use `slcan0` interface created by `slcand`
4. **Thread Safety**: Use mutexes when accessing CAN socket from multiple threads
5. **Error Handling**: Check return values and handle CAN write failures gracefully

## References

- Repository: https://github.com/Jak3Gil/Melvin_november
- Primary source: `test_motors_12_14.c`, `test_robstride_motors.c`
- Setup: `setup_usb_can_motors.sh`

