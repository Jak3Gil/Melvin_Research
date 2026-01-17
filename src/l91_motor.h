#ifndef L91_MOTOR_H
#define L91_MOTOR_H

#include <Arduino.h>

// L91 Protocol Motor Control Library
// Controls Robstride motors via serial AT commands at 921600 baud

// Motor CAN IDs (adjust as needed)
#define MOTOR_12_CAN_ID  0x0C
#define MOTOR_13_CAN_ID  0x0D
#define MOTOR_14_CAN_ID  0x0E

class L91Motor {
private:
    HardwareSerial* serial;
    int baudRate;
    
public:
    L91Motor(HardwareSerial* serialPort, int baud = 921600);
    
    // Initialize L91 serial communication
    bool begin();
    
    // Motor control commands
    bool activateMotor(uint8_t can_id);
    bool deactivateMotor(uint8_t can_id);
    bool loadParams(uint8_t can_id);
    bool moveJog(uint8_t can_id, float speed, uint8_t flag);
    
    // Helper: Send raw L91 AT command
    bool sendCommand(const uint8_t* cmd, size_t len);
    
    // Convenience methods
    bool stopMotor(uint8_t can_id);
    bool moveMotor(uint8_t can_id, float speed);
};

#endif

