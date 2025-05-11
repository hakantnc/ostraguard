// CNC Shield X ekseni pin tanımları
#define X_STEP_PIN 2
#define X_DIR_PIN 5
#define X_ENABLE_PIN 8

void setup() {
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);

  digitalWrite(X_ENABLE_PIN, LOW);  // Motoru aktif et
  digitalWrite(X_DIR_PIN, LOW);     // Saat yönü (LOW saat yönü, HIGH ters yön)

  // 20 adım at
  for (int i = 0; i < 20; i++) {
    digitalWrite(X_STEP_PIN, HIGH);
    delayMicroseconds(1500);       // Hız ayarı
    digitalWrite(X_STEP_PIN, LOW);
    delayMicroseconds(1500);
  }

  // Motoru boşa almak istersen, şu satırı ekleyebilirsin:
  // digitalWrite(X_ENABLE_PIN, HIGH);
}

void loop() {
  // boş bırak: sadece setup'ta bir kez hareket eder
  digitalWrite(X_ENABLE_PIN, LOW);  // Motoru aktif et
  digitalWrite(X_DIR_PIN, LOW);     // Saat yönü (LOW saat yönü, HIGH ters yön)

  // 20 adım at
  for (int i = 0; i < 20; i++) {
    digitalWrite(X_STEP_PIN, HIGH);
    delayMicroseconds(1500);       // Hız ayarı
    digitalWrite(X_STEP_PIN, LOW);
    delayMicroseconds(1500);
  }
}