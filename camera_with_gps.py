import serial
import pynmea2
import json
import time
import cv2
from datetime import datetime
import threading
from picamera2 import Picamera2, Preview

# GPS modülünün bağlı olduğu seri port
GPS_PORT = "/dev/ttyAMA0"  # GPS verilerinin kaydedildiği port
BAUD_RATE = 9600  # GPS'in geldiği BAUD Değeri

latest_gps_data = {"Enlem": "N/A", "Boylam": "N/A", "Yukseklik": "N/A"}

#GPS Verisini Okuma
def read_gps():
    global latest_gps_data
    try:
        with serial.Serial(GPS_PORT, BAUD_RATE, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='replace').strip()
                if line.startswith("$GPGGA"):  # GPS konum verisi
                    msg = pynmea2.parse(line)
                    latest_gps_data = {
                        "Zaman": str(msg.timestamp),
                        "Enlem": msg.latitude,
                        "Boylam": msg.longitude,
                        "Yukseklik": msg.altitude
                    }
    except Exception as e:
        print(f"GPS okuma hatası: {e}")

# GPS'i arka planda çalıştırmamızı sağlar
gps_thread = threading.Thread(target=read_gps, daemon=True)
gps_thread.start()

# Kamera Ayarları
picam2 = Picamera2()


config = picam2.create_preview_configuration(main={"size": (1280, 720)}) # Kamera Çözünürlüğü
picam2.configure(config)
picam2.start()


# Frame ve GPS verilerini eşzamanlama
while True:
    try:
        
        timestamp = datetime.now().strftime("%d.%m.%Y_%H:%M:%S")

        frame = picam2.capture_array()

        #Görüntüyü kaydet
        image_filename = f"frames/frame_{timestamp}.jpg"
        cv2.imwrite(image_filename, frame)
        print(f"Frame kaydedildi: {image_filename}")
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        # GPS verisini JSON dosyasına kaydet
        gps_data = {
            "Zaman": timestamp,
            "Enlem": latest_gps_data["Enlem"],
            "Boylam": latest_gps_data["Boylam"],
            "Yukseklik": latest_gps_data["Yukseklik"]
        }

        with open("gps_data.json", "a") as json_file:
            json.dump(gps_data, json_file, indent=4)
            json_file.write("\n")

        print(f"GPS verisi kaydedildi: {gps_data}\n")

        # Zaman ayarı
        time.sleep(1)

    except Exception as e:
        print(f"Hata oluştu: {e}")
        break

