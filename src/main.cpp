#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include "l91_motor.h"
#include "driver/twai.h"

// Servo PWM
const int servoPin = 13;
const int pwmChannel = 0;

// RGB LED pins
const int redPin = 15;
const int greenPin = 2;
const int bluePin = 4;

// MPU-6050 I2C pins
const int sdaPin = 21;
const int sclPin = 22;

// CAN Bus pins (adjust if using different GPIO)
// Note: GPIO 4 is used for blue LED, so using GPIO 18 for CAN RX instead
const int CAN_TX_PIN = 5;
const int CAN_RX_PIN = 18;  // Changed from 4 to avoid conflict with bluePin

// L91 Motor Serial (Serial2: GPIO 16=TX, 17=RX)
// Connect to L91-to-CAN adapter (CH340 USB-to-Serial at 921600 baud)

Adafruit_MPU6050 mpu;
bool mpuInitialized = false;

// L91 Motor Controller (using Serial2)
L91Motor l91Motor(&Serial2, 921600);

// CAN bus configuration
twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, TWAI_MODE_NORMAL);
twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

void setPulse(int us) {
  uint32_t duty = ((uint32_t)us * 65535) / 20000;
  ledcWrite(pwmChannel, duty);
}

void setRGB(int r, int g, int b) {
  digitalWrite(redPin, r);
  digitalWrite(greenPin, g);
  digitalWrite(bluePin, b);
}

bool initCAN() {
  // Install CAN driver
  if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
    Serial.println("CAN driver installed");
    
    // Start CAN driver
    if (twai_start() == ESP_OK) {
      Serial.println("CAN bus started (500kbps)");
      return true;
    } else {
      Serial.println("Failed to start CAN bus");
      return false;
    }
  } else {
    Serial.println("Failed to install CAN driver");
    return false;
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("ESP32 CAN-to-L91 Motor Bridge");
  Serial.println("========================================\n");
  
  // Servo PWM setup
  ledcSetup(pwmChannel, 50, 16);  // 50Hz, 16-bit
  ledcAttachPin(servoPin, pwmChannel);
  
  // RGB LED setup
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  setRGB(0, 1, 0);  // Green = ready
  
  // MPU-6050 I2C setup
  Wire.begin(sdaPin, sclPin);
  delay(100);
  
  // Scan I2C bus
  Serial.println("Scanning I2C bus...");
  byte devices = 0;
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("I2C device found at address 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
      devices++;
    }
  }
  if (devices == 0) {
    Serial.println("No I2C devices found!");
  }
  
  Serial.println("\nInitializing MPU-6050...");
  if (mpu.begin()) {
    Serial.println("MPU-6050 initialized at 0x68!");
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    mpuInitialized = true;
  } else {
    Serial.println("MPU-6050 not found! Continuing without sensor...");
    mpuInitialized = false;
  }
  
  // Initialize CAN bus
  Serial.println("\nInitializing CAN bus...");
  if (initCAN()) {
    Serial.println("✓ CAN bus ready (receiving from vision system)");
    setRGB(0, 0, 1);  // Blue = CAN ready
  } else {
    Serial.println("✗ CAN bus initialization failed");
    setRGB(1, 0, 0);  // Red = error
  }
  
  // Initialize L91 Motor Controller
  Serial.println("\nInitializing L91 Motor Controller (Serial2 @ 921600 baud)...");
  if (l91Motor.begin()) {
    Serial.println("✓ L91 Motor Controller ready");
    delay(500);
    
    // Initialize motors (activate and load params)
    Serial.println("\nInitializing Robstride motors...");
    
    // Motor 12
    Serial.print("Motor 12 (0x0C): ");
    if (l91Motor.activateMotor(MOTOR_12_CAN_ID)) {
      Serial.print("Activated, ");
      delay(200);
      if (l91Motor.loadParams(MOTOR_12_CAN_ID)) {
        Serial.println("Params loaded ✓");
      } else {
        Serial.println("Params failed ✗");
      }
    } else {
      Serial.println("Activate failed ✗");
    }
    
    // Motor 13
    Serial.print("Motor 13 (0x0D): ");
    if (l91Motor.activateMotor(MOTOR_13_CAN_ID)) {
      Serial.print("Activated, ");
      delay(200);
      if (l91Motor.loadParams(MOTOR_13_CAN_ID)) {
        Serial.println("Params loaded ✓");
      } else {
        Serial.println("Params failed ✗");
      }
    } else {
      Serial.println("Activate failed ✗");
    }
    
    // Motor 14
    Serial.print("Motor 14 (0x0E): ");
    if (l91Motor.activateMotor(MOTOR_14_CAN_ID)) {
      Serial.print("Activated, ");
      delay(200);
      if (l91Motor.loadParams(MOTOR_14_CAN_ID)) {
        Serial.println("Params loaded ✓");
      } else {
        Serial.println("Params failed ✗");
      }
    } else {
      Serial.println("Activate failed ✗");
    }
    
    setRGB(0, 1, 1);  // Cyan = motors ready
  } else {
    Serial.println("✗ L91 Motor Controller initialization failed");
    setRGB(1, 1, 0);  // Yellow = motor error
  }
  
  // Start servo at center
  setPulse(1500);
  
  Serial.println("\n========================================");
  Serial.println("System Ready!");
  Serial.println("- CAN bus: Listening for commands");
  Serial.println("- L91 Motors: Ready (Serial2 @ 921600)");
  Serial.println("========================================\n");
  
  delay(1000);
}

void processCANMessage() {
  twai_message_t message;
  
  // Try to receive CAN message (non-blocking)
  if (twai_receive(&message, pdMS_TO_TICKS(10)) == ESP_OK) {
    Serial.print("CAN RX: ID=0x");
    Serial.print(message.identifier, HEX);
    Serial.print(" DLC=");
    Serial.print(message.data_length_code);
    Serial.print(" Data=");
    
    for (int i = 0; i < message.data_length_code; i++) {
      if (message.data[i] < 0x10) Serial.print("0");
      Serial.print(message.data[i], HEX);
      Serial.print(" ");
    }
    Serial.println();
    
    // Parse CAN message and convert to L91 motor command
    // Example protocol: ID=0x0C means motor 12, data[0]=speed (-1.0 to 1.0 as byte -128 to 127)
    uint8_t motor_id = message.identifier & 0x0F;  // Extract motor ID (0x0C, 0x0D, 0x0E)
    
    if (motor_id >= 0x0C && motor_id <= 0x0E && message.data_length_code >= 1) {
      // Convert byte (-128 to 127) to float speed (-1.0 to 1.0)
      float speed = ((float)message.data[0]) / 127.0f;
      
      // Clamp to safe range
      if (speed > 1.0f) speed = 1.0f;
      if (speed < -1.0f) speed = -1.0f;
      
      Serial.print("  -> L91 Motor ");
      Serial.print(motor_id);
      Serial.print(" speed: ");
      Serial.println(speed, 3);
      
      // Send L91 command
      l91Motor.moveMotor(motor_id, speed);
    }
  }
}

void loop() {
  // Process CAN messages (non-blocking)
  processCANMessage();
  
  // Read MPU-6050 data periodically (if initialized)
  static unsigned long lastMPURead = 0;
  if (mpuInitialized && (millis() - lastMPURead > 1000)) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    
    Serial.println("=== MPU-6050 Readings ===");
    Serial.print("Accel X: "); Serial.print(a.acceleration.x);
    Serial.print("  Y: "); Serial.print(a.acceleration.y);
    Serial.print("  Z: "); Serial.println(a.acceleration.z);
    Serial.print("Gyro X: "); Serial.print(g.gyro.x);
    Serial.print("  Y: "); Serial.print(g.gyro.y);
    Serial.print("  Z: "); Serial.println(g.gyro.z);
    Serial.print("Temperature: "); Serial.print(temp.temperature); Serial.println(" C");
    Serial.println();
    
    lastMPURead = millis();
  }
  
  // Servo control (can be modified based on CAN commands if needed)
  // For now, keep existing servo behavior
  static unsigned long lastServoMove = 0;
  if (millis() - lastServoMove > 5000) {
    setPulse(1800);
    delay(2000);
    setPulse(1500);
    lastServoMove = millis();
  }
  
  // Small delay to prevent CPU spinning
  delay(10);
}
