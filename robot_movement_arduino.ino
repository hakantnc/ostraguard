// Arduino code to send motor + sensor data to Raspberry Pi 5 and receive commands
#include <Servo.h>
#include <Wire.h>
#include <MPU6050.h>

// Servo motors
Servo neckServo;
Servo headServo;
int neckAngle = 80;
int headPos = 80;

// Gyro
MPU6050 mpu;

// Ultrasonic sensors
#define trigFront 5
#define echoFront 4
#define trigRight 7
#define echoRight 6
#define trigLeft 9
#define echoLeft 8

// A4988 Step motor pins
#define STEP_L 10
#define DIR_L 11
#define STEP_R 12
#define DIR_R 13

String motorState = "STOP";
String inputCommand = "";
unsigned long lastUpdate = 0;
const unsigned long updateInterval = 300; // Send data every 300 ms

void setup() {
  Serial.begin(9600);
  Wire.begin();
  mpu.initialize();

  neckServo.attach(3);
  headServo.attach(2);
  neckServo.write(neckAngle);
  headServo.write(headPos);

  pinMode(trigFront, OUTPUT); pinMode(echoFront, INPUT);
  pinMode(trigLeft, OUTPUT);  pinMode(echoLeft, INPUT);
  pinMode(trigRight, OUTPUT); pinMode(echoRight, INPUT);

  pinMode(STEP_L, OUTPUT); pinMode(DIR_L, OUTPUT);
  pinMode(STEP_R, OUTPUT); pinMode(DIR_R, OUTPUT);
}

void loop() {
  // Check for incoming Pi commands
  if (Serial.available() > 0) {
    inputCommand = Serial.readStringUntil('\n');
    inputCommand.trim();
    handleCommand(inputCommand);
  }

  // Send sensor + motor data to Pi periodically
  unsigned long currentMillis = millis();
  if (currentMillis - lastUpdate >= updateInterval) {
    lastUpdate = currentMillis;

    float front = getDistance(trigFront, echoFront);
    float left  = getDistance(trigLeft, echoLeft);
    float right = getDistance(trigRight, echoRight);

    int16_t ax, ay, az, gx, gy, gz;
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    Serial.print("DATA:");
    Serial.print("GYRO,"); Serial.print(gx); Serial.print(","); Serial.print(gy); Serial.print(","); Serial.print(gz);
    Serial.print("|DIST,"); Serial.print(front); Serial.print(","); Serial.print(left); Serial.print(","); Serial.print(right);
    Serial.print("|STATE,"); Serial.println(motorState);
  }
}

float getDistance(int trig, int echo) {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long duration = pulseIn(echo, HIGH, 30000);
  return duration * 0.034 / 2;
}

void stepMotor(bool dirL, bool dirR, int steps = 200, int stepDelay = 800) {
  digitalWrite(DIR_L, dirL);
  digitalWrite(DIR_R, dirR);
  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_L, HIGH);
    digitalWrite(STEP_R, HIGH);
    delayMicroseconds(stepDelay);
    digitalWrite(STEP_L, LOW);
    digitalWrite(STEP_R, LOW);
    delayMicroseconds(stepDelay);
  }
}

void handleCommand(String cmd) {
  if (cmd == "CMD:FORWARD") {
    moveForward();
  } else if (cmd == "CMD:BACKWARD") {
    moveBackward();
  } else if (cmd == "CMD:LEFT") {
    turnLeft();
  } else if (cmd == "CMD:RIGHT") {
    turnRight();
  } else if (cmd == "CMD:STOP") {
    stopMotors();
  }
}

void moveForward() {
  stepMotor(HIGH, HIGH);
  motorState = "FORWARD";
}

void moveBackward() {
  stepMotor(LOW, LOW);
  motorState = "BACKWARD";
}

void turnLeft() {
  stepMotor(LOW, HIGH);
  motorState = "LEFT";
}

void turnRight() {
  stepMotor(HIGH, LOW);
  motorState = "RIGHT";
}

void stopMotors() {
  motorState = "STOP";
}