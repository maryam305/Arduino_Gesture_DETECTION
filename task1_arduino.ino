// Hand Gesture Detector - Two Sensors with Bluetooth HC-05
// Move RIGHT (left→right) = GREEN LED
// Move LEFT (right→left) = RED LED
// Stationary/Center = WHITE LED

#include <SoftwareSerial.h>

// Bluetooth HC-05 pins
#define BT_RX 2  // Connect to HC-05 TX
#define BT_TX 3  // Connect to HC-05 RX

SoftwareSerial bluetooth(BT_RX, BT_TX);

// Pin definitions
#define TRIG_L 4
#define ECHO_L 5
#define TRIG_R 11
#define ECHO_R 13

#define LAMP_RED 8
#define LAMP_WHITE 9
#define LAMP_GREEN 10

// Detection threshold (cm)
const int THRESHOLD = 30;

// State tracking
bool wasLeftActive = false;
bool wasRightActive = false;
String currentGesture = "NONE";
unsigned long gestureStartTime = 0;
const int GESTURE_HOLD_TIME = 500; // 500ms hold

void setup() {
  pinMode(TRIG_L, OUTPUT);
  pinMode(ECHO_L, INPUT);
  pinMode(TRIG_R, OUTPUT);
  pinMode(ECHO_R, INPUT);
  
  pinMode(LAMP_RED, OUTPUT);
  pinMode(LAMP_WHITE, OUTPUT);
  pinMode(LAMP_GREEN, OUTPUT);

  Serial.begin(9600);
  bluetooth.begin(9600);

  Serial.println("=== Two-Sensor Gesture Detector with Bluetooth ===");
  Serial.println("Move hand LEFT→RIGHT for GREEN");
  Serial.println("Move hand RIGHT→LEFT for RED");
  Serial.println("Stationary = WHITE");
  Serial.println("Bluetooth HC-05: RX=2, TX=3");

  // Start with all LEDs off
  digitalWrite(LAMP_RED, LOW);
  digitalWrite(LAMP_WHITE, LOW);
  digitalWrite(LAMP_GREEN, LOW);
}

void loop() {
  int leftDist = getDistance(TRIG_L, ECHO_L);
  int rightDist = getDistance(TRIG_R, ECHO_R);

  bool leftActive = (leftDist > 0 && leftDist < THRESHOLD);
  bool rightActive = (rightDist > 0 && rightDist < THRESHOLD);

  // Detect RIGHT gesture
  if (leftActive && !wasLeftActive && !rightActive) {
    // Left sensor just activated
  }
  if (leftActive && rightActive && wasLeftActive && !wasRightActive) {
    setGesture("RIGHT");
    gestureStartTime = millis();
  }

  // Detect LEFT gesture
  if (rightActive && !wasRightActive && !leftActive) {
    // Right sensor just activated
  }
  if (rightActive && leftActive && wasRightActive && !wasLeftActive) {
    setGesture("LEFT");
    gestureStartTime = millis();
  }

  // Detect CENTER / stationary
  if (leftActive && rightActive && millis() - gestureStartTime > GESTURE_HOLD_TIME) {
    setGesture("CENTER");
  }

  // No hand detected
  if (!leftActive && !rightActive && currentGesture != "NONE") {
    currentGesture = "NONE";
    turnOffAllLEDs();
    bluetooth.println("NONE");
    Serial.println("⚫ NO HAND [BT: NONE]");
  }

  wasLeftActive = leftActive;
  wasRightActive = rightActive;

  delay(50);
}

int getDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);
  int distance = duration * 0.034 / 2;
  return distance;
}

void setGesture(String gesture) {
  if (gesture == currentGesture) return;
  currentGesture = gesture;

  turnOffAllLEDs();
  bluetooth.println(gesture);

  if (gesture == "LEFT") {
    digitalWrite(LAMP_RED, HIGH);
    Serial.println("🔴 LEFT MOTION [BT: LEFT]");
  } else if (gesture == "RIGHT") {
    digitalWrite(LAMP_GREEN, HIGH);
    Serial.println("🟢 RIGHT MOTION [BT: RIGHT]");
  } else if (gesture == "CENTER") {
    digitalWrite(LAMP_WHITE, HIGH);
    Serial.println("⚪ CENTER [BT: CENTER]");
  }
}

void turnOffAllLEDs() {
  digitalWrite(LAMP_RED, LOW);
  digitalWrite(LAMP_WHITE, LOW);
  digitalWrite(LAMP_GREEN, LOW);
}
