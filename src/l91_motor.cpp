#include "l91_motor.h"

L91Motor::L91Motor(HardwareSerial* serialPort, int baud) {
    serial = serialPort;
    baudRate = baud;
}

bool L91Motor::begin() {
    serial->begin(baudRate, SERIAL_8N1);
    delay(100);  // Allow serial to initialize
    serial->flush();
    return true;
}

bool L91Motor::sendCommand(const uint8_t* cmd, size_t len) {
    serial->flush();  // Clear any pending data
    
    size_t written = serial->write(cmd, len);
    if (written != len) {
        Serial.print("L91: Write failed (expected ");
        Serial.print(len);
        Serial.print(", got ");
        Serial.println(written);
        return false;
    }
    
    serial->flush();  // Wait for transmission to complete
    delay(10);  // 10ms delay after command
    return true;
}

bool L91Motor::activateMotor(uint8_t can_id) {
    // Format: AT 00 07 e8 <can_id> 01 00 0d 0a
    uint8_t cmd[] = {0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a};
    bool result = sendCommand(cmd, sizeof(cmd));
    delay(200);  // Wait for motor to activate
    return result;
}

bool L91Motor::deactivateMotor(uint8_t can_id) {
    // Format: AT 00 07 e8 <can_id> 00 00 0d 0a
    uint8_t cmd[] = {0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a};
    bool result = sendCommand(cmd, sizeof(cmd));
    delay(100);
    return result;
}

bool L91Motor::loadParams(uint8_t can_id) {
    // Format: AT 20 07 e8 <can_id> 08 00 c4 00 00 00 00 00 00 0d 0a
    uint8_t cmd[] = {0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a};
    bool result = sendCommand(cmd, sizeof(cmd));
    delay(200);
    return result;
}

bool L91Motor::moveJog(uint8_t can_id, float speed, uint8_t flag) {
    // Format: AT 90 07 e8 <can_id> 08 05 70 00 00 07 <flag> <speed_bytes> 0d 0a
    uint8_t cmd[20];
    int idx = 0;
    
    cmd[idx++] = 0x41;  // 'A'
    cmd[idx++] = 0x54;  // 'T'
    cmd[idx++] = 0x90;  // Command type (MOVE_JOG)
    cmd[idx++] = 0x07;  // Address high
    cmd[idx++] = 0xe8;  // Address low (0x07e8)
    cmd[idx++] = can_id;  // Motor CAN ID
    cmd[idx++] = 0x08;  // Data length
    cmd[idx++] = 0x05;  // Command high
    cmd[idx++] = 0x70;  // Command low (MOVE_JOG = 0x0570)
    cmd[idx++] = 0x00;  // Fixed
    cmd[idx++] = 0x00;  // Fixed
    cmd[idx++] = 0x07;  // Fixed
    cmd[idx++] = flag;  // 0=stop, 1=move
    
    // Speed encoding (16-bit signed, where 0x7fff = 0.0)
    int16_t speed_val;
    if (speed == 0.0f) {
        speed_val = 0x7fff;  // Stop
    } else if (speed > 0.0f) {
        // Positive speed: scale factor ~3283.0
        speed_val = 0x8000 + (int16_t)(speed * 3283.0f);
    } else {
        // Negative speed
        speed_val = 0x7fff + (int16_t)(speed * 3283.0f);
    }
    
    cmd[idx++] = (speed_val >> 8) & 0xFF;  // High byte
    cmd[idx++] = speed_val & 0xFF;         // Low byte
    cmd[idx++] = 0x0d;  // \r
    cmd[idx++] = 0x0a;  // \n
    
    return sendCommand(cmd, idx);
}

bool L91Motor::stopMotor(uint8_t can_id) {
    return moveJog(can_id, 0.0f, 0);
}

bool L91Motor::moveMotor(uint8_t can_id, float speed) {
    uint8_t flag = (speed == 0.0f) ? 0 : 1;
    return moveJog(can_id, speed, flag);
}

