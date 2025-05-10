import serial
import os
import time
import psutil
import subprocess
import threading

# ---------- AYARLAR ----------
# Arduino için seri port ayarları (port ve baud rate cihazınızla uyumlu olmalı)
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=0.5)

# Temel hedef dizini: Bu dizinde günlük bazda alt klasörler oluşturulacak.
target_path = "/home/mergen/Desktop/week 9 Burak"

# ---------- GÜNLÜK KLASÖR OLUŞTURMA ----------
def get_daily_folder():
    current_date = time.strftime("%Y-%m-%d")
    daily_folder = os.path.join(target_path, current_date)
    if not os.path.exists(daily_folder):
        os.makedirs(daily_folder)
    return daily_folder

def get_daily_photo_folder():
    current_date = time.strftime("%Y-%m-%d")
    photo_folder = os.path.join(target_path, current_date + "_Photo")
    if not os.path.exists(photo_folder):
        os.makedirs(photo_folder)
    return photo_folder

# Log dosyası: Günlük klasör içinde "terminal_log.txt" adlı dosyaya ekleme yapılacak.
def get_log_filepath():
    folder = get_daily_folder()
    return os.path.join(folder, "terminal_log.txt")

# ---------- SİSTEM VERİLERİ ----------
def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000.0
        return f"{temp:.1f}°C"
    except:
        return "N/A"

def get_gpu_usage():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        temp = output.strip().split('=')[1]
        return temp
    except:
        return "N/A"

def get_system_stats():
    cpu_percent = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    ram_used = ram.used / (1024 * 1024)  # MB cinsinden
    return {
        "CPU": f"{cpu_percent:.1f}%",
        "RAM": f"{ram_used:.1f} MB",
        "CPU Temp": get_cpu_temp(),
        "GPU Temp": get_gpu_usage()
    }

# ---------- ARDUINO VERİLERİNİN AYRIŞTIRILMASI ----------
def parse_data(line):
    """
    Arduino tarafından gönderilen satırı parçalayıp verileri sözlük şeklinde toplar.
    Beklenen format:
    DATA:Gyro=xxx,yyy,zzz | ServoAngles=neck,head | Distance(cm)=Front:xxx Left:xxx Right:xxx | MotorState=STATE
    """
    if line.startswith("DATA:"):
        data_str = line[5:]
    else:
        data_str = line

    parts = data_str.split(" | ")
    parsed = {}
    for part in parts:
        if part.startswith("Gyro="):
            gyro_vals = part[len("Gyro="):].split(",")
            if len(gyro_vals) >= 3:
                parsed["Gyro X"] = gyro_vals[0]
                parsed["Gyro Y"] = gyro_vals[1]
                parsed["Gyro Z"] = gyro_vals[2]
        elif part.startswith("ServoAngles="):
            servo_vals = part[len("ServoAngles="):].split(",")
            if len(servo_vals) >= 2:
                parsed["Neck Servo"] = servo_vals[0]
                parsed["Head Servo"] = servo_vals[1]
        elif part.startswith("Distance(cm)="):
            distances = part[len("Distance(cm)="):].split(" ")
            for token in distances:
                if token.startswith("Front:"):
                    parsed["Front Distance"] = token[len("Front:"):]
                elif token.startswith("Left:"):
                    parsed["Left Distance"] = token[len("Left:"):]
                elif token.startswith("Right:"):
                    parsed["Right Distance"] = token[len("Right:"):]
        elif part.startswith("MotorState="):
            parsed["Motor State"] = part[len("MotorState="):]
    return parsed

# ---------- FOTOĞRAF ÇEKME FONKSİYONU ----------
def photo_capturer():
    """
    Ayrı bir thread içinde, kod çalıştığı sürece saniyenin onda biri oranında fotoğraf çeker.
    Her çekim, o anki günlük fotoğraf klasörüne "photo_YYYYMMDD_HHMMSS_mmm.jpg" adıyla kaydedilir.
    """
    while True:
        folder = get_daily_photo_folder()  # Günlük fotoğraf klasörü (örneğin "2025-04-12_Photo")
        t = time.time()
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(t))
        ms = int((t - int(t)) * 1000)  # milisaniye kısmı
        full_timestamp = f"{timestamp}_{ms:03d}"
        photo_filepath = os.path.join(folder, f"photo_{full_timestamp}.jpg")
        command = f"libcamera-still -o '{photo_filepath}' -t 1 --nopreview"
        subprocess.call(command, shell=True)
        time.sleep(0.1)

# Fotoğraf çekme thread'ini başlatıyoruz.
photo_thread = threading.Thread(target=photo_capturer, daemon=True)
photo_thread.start()

# ---------- ANA DÖNGÜ VE LOG KAYDI ----------
latest_data = None
arduino_last_update = 0
log_last_save = 0

try:
    while True:
        current_time = time.time()
        
        if current_time - arduino_last_update >= 15:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode("utf-8").strip()
                except UnicodeDecodeError:
                    line = ""
                if line.startswith("DATA:"):
                    latest_data = parse_data(line)
            arduino_last_update = current_time

        system_stats = get_system_stats()

        output_str = ""
        output_str += "=== RASPBERRY PI SYSTEM STATS ===\n\n"
        output_str += f"CPU Usage   : {system_stats['CPU']}\n"
        output_str += f"RAM Usage   : {system_stats['RAM']}\n"
        output_str += f"CPU Temp    : {system_stats['CPU Temp']}\n"
        output_str += f"GPU Temp    : {system_stats['GPU Temp']}\n\n"
        output_str += "=== ARDUINO SENSOR DATA (15 saniyede bir güncelleniyor) ===\n\n"
        if latest_data:
            if "Gyro X" in latest_data:
                output_str += f"Gyro X      : {latest_data['Gyro X']}\n"
                output_str += f"Gyro Y      : {latest_data['Gyro Y']}\n"
                output_str += f"Gyro Z      : {latest_data['Gyro Z']}\n"
            if "Neck Servo" in latest_data:
                output_str += f"Neck Servo  : {latest_data['Neck Servo']}\n"
            if "Head Servo" in latest_data:
                output_str += f"Head Servo  : {latest_data['Head Servo']}\n"
            if "Front Distance" in latest_data:
                output_str += f"Front Dist. : {latest_data['Front Distance']} cm\n"
            if "Left Distance" in latest_data:
                output_str += f"Left Dist.  : {latest_data['Left Distance']} cm\n"
            if "Right Distance" in latest_data:
                output_str += f"Right Dist. : {latest_data['Right Distance']} cm\n"
            if "Motor State" in latest_data:
                output_str += f"Motor State : {latest_data['Motor State']}\n"
        else:
            output_str += "Henüz Arduino verisi alınmadı...\n"

        update_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(arduino_last_update))
        output_str += f"\nSon Arduino Güncellemesi: {update_time_str}\n"
        output_str += "\n(Terminal her 0.5 saniyede güncelleniyor. Çıkmak için Ctrl+C'ye basın.)\n"

        os.system('clear')
        print(output_str)

        if current_time - log_last_save >= 15:
            log_filepath = get_log_filepath()
            with open(log_filepath, "a") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
                f.write(f"\n--- {timestamp} ---\n")
                f.write(output_str)
            log_last_save = current_time

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nÇıkılıyor...")
