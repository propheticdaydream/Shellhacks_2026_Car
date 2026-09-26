const int stepPin = D0; 
const int dirPin = D1;

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
}

void loop() {
  unsigned long startTime;

  // ---------------------------------------------
  // Spin Clockwise for 5 seconds
  // ---------------------------------------------
  digitalWrite(dirPin, HIGH);
  startTime = millis(); // Record the current time in milliseconds

  // Keep stepping as long as the elapsed time is less than 5000ms
  while (millis() - startTime < 5000) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(1000);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(1000);
  }

  // Pause for 1 second
  delay(1000); 

  // ---------------------------------------------
  // Spin Counter-Clockwise for 5 seconds (Faster)
  // ---------------------------------------------
  digitalWrite(dirPin, LOW);
  startTime = millis(); // Reset the start time for the second half

  while (millis() - startTime < 5000) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(500);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(500);
  }

  // Pause for 1 second before the cycle repeats
  delay(1000);

  // (Optional) If you want the cycle to run just once and stop, 
  // uncomment the next three lines:
  // while(true) {
  //   // Trapped here forever
  // }
}
