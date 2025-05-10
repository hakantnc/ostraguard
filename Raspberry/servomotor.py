import serial
import time

# servo motor 9. pine bağlı
# Arduino'nun bağlı olduğu portu ayarla
PORT = "/dev/ttyACM0"  # Gerekirse /dev/ttyUSB0 olarak değiştir
BAUDRATE = 9600  # Arduino ile haberleşme baud hızı

try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)  # Seri bağlantıyı başlat
    time.sleep(2)  # Bağlantının oturması için bekleme süresi
    print("Arduino bağlantısı kuruldu!")
except serial.SerialException:
    print("Arduino'ya bağlanılamadı! Doğru portu kullandığınızdan emin olun.")
    exit()

try:
    while True:
        aci = input("Servo için açı (20-160): ")  # Kullanıcıdan açı al
        if aci.isdigit():  # Girilen değer sayı mı?
            aci = int(aci)
            if 20 <= aci <= 160:
                ser.write(f"{aci}\n".encode())  # Arduino'ya açı gönder
                time.sleep(0.5)  # Arduino'nun yanıt vermesi için bekleme süresi
                gelen_veri = ser.readline().decode('utf-8').strip()
                print(f"Arduino Yanıtı: {gelen_veri}")
            else:
                print("Hata: Açı 20-160 arasında olmalı!")
        else:
            print("Hata: Lütfen geçerli bir sayı girin!")

except KeyboardInterrupt:
    print("Çıkış yapılıyor...")
    ser.close()
