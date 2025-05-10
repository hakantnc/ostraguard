import serial
import json
import os
import time
import psutil
from datetime import datetime

# === Raspberry Pi - Arduino Seri Bağlantı Ayarları ===
SERIAL_PORT = '/dev/ttyUSB0'  # Gerekirse /dev/ttyACM0 veya farklı bir port olabilir
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"[+] Arduino ile bağlantı kuruldu: {SERIAL_PORT}")
except Exception as e:
    print(f"[!] Arduino seri portuna bağlanılamadı: {e}")
    exit()

# === Klasör Ayarları ===
LOG_DIR = "logs"
PENDING_DIR = os.path.join(LOG_DIR, "pending")

def ensure_dirs():
    os.makedirs(PENDING_DIR, exist_ok=True)

ensure_dirs()

# === JSON Verilerini Yaz ===
def write_json(data, path):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[!] JSON yazma hatası: {e}")

def get_pending_log_path(filename):
    return os.path.join(PENDING_DIR, filename)

# === Arduino'dan Gelen Verileri Ayrıştır ===
def parse_arduino(line):
    if not line.startswith("DATA:"):
        return {}

    result = {}
    try:
        raw = line.replace("DATA:", "")
        parts = raw.split("|")
        for p in parts:
            key, values = p.split(",", 1)
            result[key] = [float(v) if "." in v else int(v) for v in values.split(",")]
    except Exception as e:
        print(f"[!] Ayrıştırma hatası: {e}")
    return result

# === Pi5 Sistem Durumunu Al ===
def get_system_stats():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "disk_percent": disk.percent,
        "time": datetime.now().isoformat()
    }

# === Arduino'ya Komut Gönder ===
def komut_gonder(komut):
    try:
        ser.write((komut + '\n').encode())
        print(f"[Sent] {komut}")
        time.sleep(0.1)
    except Exception as e:
        print(f"[!] Komut gönderilemedi: {e}")

# === Arduino'dan Veri Oku ===
def veri_oku():
    try:
        if ser.in_waiting > 0:
            return ser.readline().decode().strip()
    except Exception as e:
        print(f"[!] Veri okunamadı: {e}")
    return None

# === Ana Döngü ===
def main_loop():
    last_a = last_p = last_cmd = 0
    komut_durumu = "FORWARD"  # Başlangıç komutu

    while True:
        now = time.time()

        # Arduino'dan veri oku
        if now - last_a >= 5:
            line = veri_oku()
            if line and line.startswith("DATA:"):
                parsed = parse_arduino(line)
                fname = f"Arduino_{datetime.now():%Y%m%d_%H%M%S}.json"
                path = get_pending_log_path(fname)
                write_json(parsed, path)
                print(f"[Arduino] Kayıt alındı → {fname}")
            elif line:
                print(f"[Arduino] Gelen veri: {line}")
            last_a = now

        # Raspberry Pi sistem bilgilerini kaydet
        if now - last_p >= 5:
            stats = get_system_stats()
            fname = "Pi5_Latest.json"
            path = get_pending_log_path(fname)
            write_json(stats, path)
            print("[Pi5] Sistem bilgisi kaydedildi.")
            last_p = now

        # Arduino’ya otomatik komut gönder (FORWARD ve STOP arasında dönüşümlü)
        if now - last_cmd >= 10:
            komut_gonder(f"CMD:{komut_durumu}")
            print(f"[Oto Komut] Gönderildi: CMD:{komut_durumu}")
            komut_durumu = "STOP" if komut_durumu == "FORWARD" else "FORWARD"
            last_cmd = now

        time.sleep(0.5)

# === Başlat ===
if _name_ == '_main_':
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n[!] Program sonlandırıldı.")
        ser.close()