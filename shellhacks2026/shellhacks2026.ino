#include <Wire.h>

// 7-bit I2C address of MPU-6050 (when AD0 is connected to GND)
const uint8_t MPU_ADDR = 0x68;

// Buffer to store the 6 incoming raw data bytes (2 bytes per axis)
uint8_t buffer[6];

// Array to hold the reconstructed 16-bit signed axis values
int16_t data[3];

// Variables holding the individual X, Y, and Z readings
int x, y, z;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  while (!Serial && millis() < 3000); // Wait up to 3 seconds for USB Serial connection

  // Initialize I2C Bus 2 on Teensy 4.1 (SDA2 = Pin 25, SCL2 = Pin 24)
  Wire2.begin();
  Wire2.setClock(400000); // Set bus to 400 kHz fast mode

  // Wake up the MPU-6050 (clears default sleep bit in PWR_MGMT_1)
  Wire2.beginTransmission(MPU_ADDR);
  Wire2.write(0x6B); // PWR_MGMT_1 register address
  Wire2.write(0x00); // Write 0 to wake sensor up
  Wire2.endTransmission();
}

void loop() {
  Serial.println("Boot OK");
  // put your main code here, to run repeatedly:
  delay(200); // Sample delay matching wait_us(200000)

  // Point to the starting register for accelerometer data
  Wire2.beginTransmission(MPU_ADDR);
  Wire2.write(0x3B); // ACCEL_XOUT_H register
  Wire2.endTransmission(false); // Repeated start condition to hold the bus

  // Request 6 consecutive bytes from MPU-6050
  Wire2.requestFrom(MPU_ADDR, (uint8_t)6);

  if (Wire2.available() == 6) {
    // Read the 6 raw bytes into the buffer
    for (int i = 0; i < 6; i++) {
      buffer[i] = Wire2.read();
    }

    // Combine High and Low bytes (MPU-6050 outputs Big-Endian)
    data[0] = (buffer[0] << 8) | buffer[1]; // X-axis
    data[1] = (buffer[2] << 8) | buffer[3]; // Y-axis
    data[2] = (buffer[4] << 8) | buffer[5]; // Z-axis

    // Assign data values to each direction
    x = data[0];
    y = data[1];
    z = data[2];

    // Print values to Serial Monitor matching original lab formatting
    Serial.printf("x=");
    Serial.printf("%d",x);
    Serial.printf(" y=");
    Serial.printf("%d ", y);
    Serial.printf(" z=");
    Serial.printf("%d ", z);
  }

  delay(1000); // 1-second delay matching wait_us(1000000)
}
