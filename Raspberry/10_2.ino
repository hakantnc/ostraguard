#include <Servo.h>
#include <Wire.h>
#include <MPU6050.h>

// === Servo motorlar ===
Servo neckServo;
Servo headServo;
int neckAngle = 80;
int headPos = 80;

// === Gyro ===
MPU6050 mpu;

// === Ultrasonik sensörler ===
#define trigFront 5
#define echoFront 4
#define trigRight 7
#define echoRight 6
#define trigLeft 9
#define echoLeft 8

// === A4988 Step motor pinleri ===
#define STEP_L 10   // Sol motor STEP
#define DIR_L 11    // Sol motor DIR
#define STEP_R 12   // Sağ motor STEP
#define DIR_R 13    // Sağ motor DIR
// #define EN 14     // Enable pini (LOW → Aktif) — opsiyonel

// === Global ===
String motorState = "STOP";
String inputCommand = "";
unsigned long lastUpdate = 0;
const unsigned long updateInterval = 300; // 300 ms

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
  // pinMode(EN, OUTPUT); digitalWrite(EN, LOW); // opsiyonel
}

void loop() {
  // === Pi'den komut varsa oku ===
  if (Serial.available() > 0) {
    inputCommand = Serial.readStringUntil('\n');
    inputCommand.trim();
    handleCommand(inputCommand);
  }

  // === Sensör verisi gönderimi ===
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

// === Mesafe ölçümü ===
float getDistance(int trig, int echo) {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long duration = pulseIn(echo, HIGH, 30000);
  return duration * 0.034 / 2;
}

// === Step motor kontrolü ===
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

// === Komutları işle ===
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

// === Hareket fonksiyonları ===
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
