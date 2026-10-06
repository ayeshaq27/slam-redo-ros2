// Resting state: robot stays still.
// Stops all motors, centres the ultrasonic servo, then does nothing.
// Upload this whenever you want the robot parked.
#include <Arduino.h>
#include "Freenove_4WD_Car_For_Pico_W.h"

void setup() {
  Motor_Setup();          // Freenove: set up the motor pins
  Motor_Move(0, 0); // all four wheels at speed 0

  Servo_Setup();          // Freenove: set up the servo
  Servo_1_Angle(90);      // point the ultrasonic sensor straight ahead
}

void loop() {
  // Intentionally empty: nothing runs, so nothing moves.
}
