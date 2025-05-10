import serial
import pynmea2

# GPS modülünün bağlı olduğu seri port (Raspberry Pi 5 için genellikle /dev/serial0 veya /dev/ttyAMA0 olur)
GPS_PORT = "/dev/ttyAMA0"
BAUD_RATE = 9600  # GPS modülünün baud rate değeri (genellikle 9600 veya 115200 olur)

def read_gps():
    try:
       with serial.Serial(GPS_PORT, BAUD_RATE, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='replace')  # GPS verisini oku
                if line.startswith("$GPGGA"):  # En yaygın GPS formatı (konum verisi)
                    msg = pynmea2.parse(line)
                    print(f"Zaman: {msg.timestamp}, Enlem: {msg.latitude} {msg.lat_dir}, Boylam: {msg.longitude} {msg.lon_dir}, Yükseklik: {msg.altitude}m")
    except Exception as e:
        print(f"GPS okuma hatası: {e}")

if __name__ == "__main__":
    read_gps()
