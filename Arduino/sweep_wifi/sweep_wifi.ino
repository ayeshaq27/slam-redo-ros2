// Sweep + WiFi: sweeps the ultrasonic servo and sends "angle,distance_cm" lines
// over TCP to whoever connects (our ROS2 sweep_scan_node on the Mac).

#include <Arduino.h>
#include <WiFi.h>
#include "Freenove_4WD_Car_For_Pico_W.h"   // Servo_Setup(), Servo_1_Angle(), Ultrasonic_Setup(), Get_Sonar()
#include "secrets.h"                        // WIFI_SSID and WIFI_PASSWORD (not committed to git)

// ---- WiFi / TCP ----
#define PORT 4002
const char *ssid_Router     = WIFI_SSID;       // set in secrets.h
const char *password_Router = WIFI_PASSWORD;   // set in secrets.h
WiFiServer server(PORT);

// ---- Sweep settings ----
const int MIN_ANGLE = 30;    // servo angle pointing right
const int MAX_ANGLE = 150;   // servo angle pointing left
const int STEP      = 15;    // degrees moved between readings
const int SETTLE_MS = 150;   // wait after moving, so the servo arrives and old echoes die out

void setup() {
  Serial.begin(115200);
  delay(1000);

  Ultrasonic_Setup();
  Servo_Setup();
  Servo_1_Angle(90);   // rest at centre until someone connects

  Serial.print("Connecting to ");
  Serial.println(ssid_Router);
  WiFi.disconnect();
  WiFi.begin(ssid_Router, password_Router);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.printf("Port: %d\n", PORT);

  server.begin(PORT);
}

void loop() {
  WiFiClient client = server.accept();   // wait for the ROS2 node to connect
  if (!client) return;

  Serial.println("Client connected - starting sweep.");

  // Every new connection starts a fresh sweep from the right-hand end
  int angle = MIN_ANGLE;
  int direction = 1;
  Servo_1_Angle(angle);
  delay(500);   // big first move, extra time

  while (client.connected()) {
    // 1. Move, then wait for the servo to get there
    Servo_1_Angle(angle);
    delay(SETTLE_MS);

    // 2. Read and send "angle,distance_cm"
    float distance = Get_Sonar();
    client.print(String(angle) + "," + String(distance) + "\n");

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

  client.stop();
  Servo_1_Angle(90);   // back to centre when the node disconnects
  Serial.println("Client disconnected.");
}
