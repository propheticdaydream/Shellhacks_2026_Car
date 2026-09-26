#include <ps5Controller.h>
#include <SPI.h>

// ESP32 SPI pins
#define SCK_PIN   18
#define MISO_PIN  19
#define MOSI_PIN  23
#define CS_PIN     5

SPISettings spiSettings(1000000, MSBFIRST, SPI_MODE0);

void setup() {
  Serial.begin(115200);
  delay(2000);

  pinMode(CS_PIN, OUTPUT);
  digitalWrite(CS_PIN, HIGH);

  //setup for spi
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, CS_PIN);

  Serial.println("Starting Bluetooth...");

  ps5.begin(20);

  Serial.println("Bluetooth started.");
  Serial.println("Waiting for PS5 controller...");
}

void sendMotorValues(uint8_t left, uint8_t right) {

  SPI.beginTransaction(spiSettings);

  digitalWrite(CS_PIN, LOW);

  // Packet:
  // 0xAA | Left | Right | Checksum
  SPI.transfer(0xAA);
  SPI.transfer(left);
  SPI.transfer(right);

  uint8_t checksum = 0xAA ^ left ^ right;
  SPI.transfer(checksum);

  digitalWrite(CS_PIN, HIGH);

  SPI.endTransaction();
}

void loop() {

  if (ps5.isConnected()) {

    uint8_t leftMotor  = ps5.l2;
    uint8_t rightMotor = ps5.r2;

    sendMotorValues(leftMotor, rightMotor);

    Serial.print("L2: ");
    Serial.print(leftMotor);

    Serial.print("  R2: ");
    Serial.println(rightMotor);

  } else {

    Serial.println("Waiting for PS5 controller...");
  }

  delay(10);
}