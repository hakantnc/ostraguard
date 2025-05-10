import serial
import time

# Arduino'nun bağlı olduğu USB portu kontrol et!
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Gerekirse /dev/ttyUSB0 olarak değiştir
time.sleep(2)  # Bağlantı için bekleme

try:
    while True:
        if ser.in_waiting > 0:
            mesafe = ser.readline().decode('utf-8').strip()
            print(f"Alınan Mesafe: {mesafe} cm")
        
        time.sleep(0.5)  # Yükü azaltmak için kısa bekleme süresi

except KeyboardInterrupt:
    print("Çıkış yapılıyor...")
    ser.close()
