import serial
import time

arduino_port = '/dev/ttyACM0'  # Port Raspberry Pi'ye göre değişebilir
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)

def read_serial_data():
    last_print = time.time()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            last_print = time.time()

            if line.startswith("MOTOR:"):
                hareket = line.split("MOTOR:")[1]
                print(f"[MOTOR] {hareket}")

            elif line.startswith("SERVO:"):
                aci = line.split("SERVO:")[1]
                print(f"[SERVO] {aci}")

            elif line.startswith("Distance:"):
                mesafe = line.split("Distance:")[1]
                print(f"[MESAFE] {mesafe.strip()}")

            else:
                print(f"[GENEL VERİ] {line}")

        else:
            if time.time() - last_print > 2:
                print("[BEKLİYOR] Veri bekleniyor...")
                last_print = time.time()
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        print("Arduino'dan gelen veriler:")
        read_serial_data()
    except KeyboardInterrupt:
        print("Program sonlandırıldı.")
        ser.close()
