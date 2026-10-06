// Servo sweep + ultrasonic test (no WiFi, no ROS2)
// Moves the servo step by step, takes one distance reading at each angle,
// and prints "angle,distance" to the Serial Monitor.
// Uses Freenove's library for both the servo and the ultrasonic sensor.
#include <Arduino.h>
#include "Freenove_4WD_Car_For_Pico_W.h"   // gives us Servo_Setup(), Servo_1_Angle(), Ultrasonic_Setup(), Get_Sonar()


// ---- Sweep settings ----
const int MIN_ANGLE = 30;    // leftmost angle
const int MAX_ANGLE = 150;   // rightmost angle
const int STEP      = 15;    // degrees moved between readings
const int SETTLE_MS = 150;   // wait after moving, so the servo arrives and old echoes die out

int angle = MIN_ANGLE;
int direction = 1;   // 1 = sweeping right, -1 = sweeping left

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) {}  // wait briefly for the Serial Monitor

  Ultrasonic_Setup();     // Freenove: set up the ultrasonic sensor pins
  Servo_Setup();         // Freenove: set up the servo
  Servo_1_Angle(90);     // start at centre
  delay(500);            // first move can be big, so give it extra time

  Serial.println("angle,distance_cm");
}

void loop() {
  // 1. Move, then wait for the servo to get there
  Servo_1_Angle(angle);
  delay(SETTLE_MS);

  // 2. Read and print
  float distance = Get_Sonar();
  Serial.print(angle);
  Serial.print(",");
  Serial.println(distance);

  // 3. Pick the next angle, turning around at each end
  angle += direction * STEP;
  if (angle > MAX_ANGLE) {
    angle = MAX_ANGLE - STEP;
    direction = -1;
  } else if (angle < MIN_ANGLE) {
    angle = MIN_ANGLE + STEP;
    direction = 1;
  } 
}
