import serial
import time

# Seri port ayarları.
PORT = devttyACM0  # Arduino'nun bağlı olduğu port
BAUDRATE = 9600
SON_DURUM = DUR  # Başlangıç durumu

try
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)  # Bağlantı oturması için bekle
    print(Arduino bağlantısı kuruldu)
except serial.SerialException
    print(Arduino'ya bağlanılamadı. Doğru portu kullandığınızdan emin olun.)
    exit()

try
    while True
        # Arduino'dan mesafe verisini oku
        mesafe_veri = ser.readline().decode('utf-8').strip()

        if mesafe_veri.startswith(Mesafe)
            try
                mesafe = float(mesafe_veri.split()[1].strip())
                print(Okunan Mesafe, mesafe, cm)

                # Mesafeye göre motor durumu belirle
                if mesafe = 10 and SON_DURUM != GERI
                    SON_DURUM = GERI
                    print(Mesafe = 10 cm, motor geri gidiyor...)
                    ser.write(GERIn.encode())
                    time.sleep(1)

                elif 10  mesafe = 20 and SON_DURUM != DUR
                    SON_DURUM = DUR
                    print(Mesafe 10-20 cm, motor duruyor...)
                    ser.write(DURn.encode())
                    time.sleep(1)

                elif mesafe  20 and SON_DURUM != ILER
                    SON_DURUM = ILER
                    print(Mesafe 20 cm'den büyük, motor ileri gidiyor...)
                    ser.write(ILERIn.encode())
                    time.sleep(1)

            except ValueError
                pass  # Geçersiz veri gelirse görmezden gel

except KeyboardInterrupt
    print(Çıkış yapılıyor...)
    ser.close()
