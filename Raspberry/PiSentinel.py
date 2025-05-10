# -*- coding: utf-8 -*-
#!/usr/bin/python3

import serial
import os
import time
import psutil
import subprocess
import threading
import json
import requests
from datetime import datetime

# ==== AYARLAR ====
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=0.5)

base_path     = "/home/mergen/Desktop/Week 10 Burak"
alert_path    = os.path.join(base_path, "Incoming", "Alerts")
PI4_API       = "http://10.146.40.94:8000/alerts"
alert_counter = 1

pi4_user      = "mergen"
pi4_ip        = "10.146.40.94"
pi4_dest_base = "/home/mergen/Desktop/db"

# ==== KLASÖRLER ====
def ensure_dirs():
    os.makedirs(os.path.join(base_path, "Pending", "Images"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "Pending", "Logs"), exist_ok=True)
    os.makedirs(alert_path, exist_ok=True)

def get_pending_image_path(filename):
    return os.path.join(base_path, "Pending", "Images", filename)

def get_pending_log_path(filename):
    return os.path.join(base_path, "Pending", "Logs", filename)

# ==== JSON ====
def write_json(data, path, mode="w"):
    with open(path, mode, encoding="utf-8") as f:
        if mode == "a":
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        else:
            json.dump(data, f, indent=4, ensure_ascii=False)

# ==== SCP GÖNDER ====
def send_file_to_pi4(local_path, remote_folder):
    filename = os.path.basename(local_path)
    remote_path = f"{pi4_user}@{pi4_ip}:{pi4_dest_base}/{remote_folder}/{filename}"
    try:
        result = subprocess.run(
            ["scp", local_path, remote_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        if result.returncode == 0:
            os.remove(local_path)
            print(f"[✓] Sent and deleted → {remote_folder}/{filename}")
        else:
            print(f"[!] Failed to send: {filename}\n{result.stderr.decode().strip()}")
    except Exception as e:
        print(f"[!] Exception during send: {e}")

# ==== SİSTEM VERİLERİ ====
def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return f"{int(f.read())/1000.0:.1f}°C"
    except:
        return "N/A"

def get_gpu_temp():
    try:
        out = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return out.strip().split('=')[1]
    except:
        return "N/A"

def get_network_speeds():
    net1 = psutil.net_io_counters()
    time.sleep(1)
    net2 = psutil.net_io_counters()
    up   = (net2.bytes_sent - net1.bytes_sent)/1024
    down = (net2.bytes_recv - net1.bytes_recv)/1024
    return {"Upload (KB/s)": f"{up:.2f}", "Download (KB/s)": f"{down:.2f}"}

def get_system_stats():
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().used/(1024*1024)
    net = get_network_speeds()
    return {
        "CPU": f"{cpu:.1f}%",
        "RAM": f"{ram:.1f} MB",
        "CPU Temp": get_cpu_temp(),
        "GPU Temp": get_gpu_temp(),
        **net,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ==== ARDUINO VERİLERİNİ AYIKLA ====
def parse_arduino(line):
    data = {}
    parts = line.replace("DATA:", "").split(" | ")
    for part in parts:
        if part.startswith("Gyro="):
            gx, gy, gz = part.split("=")[1].split(",")
            data["Gyro"] = {"X": gx, "Y": gy, "Z": gz}
        elif part.startswith("ServoAngles="):
            n, h = part.split("=")[1].split(",")
            data["ServoAngles"] = {"Neck": n, "Head": h}
        elif part.startswith("Distance(cm)="):
            d = part.split("=")[1].split(" ")
            data["Distances"] = {kv.split(":")[0]: kv.split(":")[1] for kv in d}
        elif part.startswith("MotorState="):
            data["MotorState"] = part.split("=")[1]
    data["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

# ==== FOTOĞRAF THREAD ====
def photo_loop():
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename  = f"photo_{timestamp}.jpg"
        path      = get_pending_image_path(filename)
        cmd       = f"libcamera-still -o '{path}' -t 1 --width 1920 --height 1080 --nopreview"
        subprocess.call(cmd, shell=True)
        print(f"[Frame] Captured → {filename}")
        threading.Thread(target=send_file_to_pi4, args=(path, "Images"), daemon=True).start()
        time.sleep(1)

# ==== DOSYA GÖNDERİM THREAD ====
def retry_pending_loop():
    while True:
        for folder, remote in [("Images","Images"),("Logs","Logs")]:
            pending_dir = os.path.join(base_path, "Pending", folder)
            for file in os.listdir(pending_dir):
                local = os.path.join(pending_dir, file)
                threading.Thread(target=send_file_to_pi4, args=(local, remote), daemon=True).start()
        time.sleep(15)

# ==== ALERT SİSTEMİ ====
def handle_alert_command(cmd):
    try:
        t = cmd["type"]
        v = cmd["value"]
        if t == "motor":
            serial_cmd = f"CMD:MOTOR={v}\n"
        else:
            serial_cmd = f"CMD:SERVO={v}\n"
        print(f"[Alert] Arduino'ya gönderiliyor → {serial_cmd.strip()}")
        ser.write(serial_cmd.encode())
    except Exception as e:
        print(f"[!] Alert işlenemedi: {e}")

def alert_listener():
    global alert_counter
    ensure_dirs()
    while True:
        try:
            resp = requests.get(PI4_API, timeout=10)
            if resp.status_code == 200:
                alerts = resp.json()
                if alerts:
                    fname = f"Alerts{alert_counter}.json"
                    fpath = os.path.join(alert_path, fname)
                    with open(fpath, "w", encoding="utf-8") as jf:
                        json.dump(alerts, jf, indent=4, ensure_ascii=False)
                    print(f"[✓] Alert kaydedildi: {fname}")
                    for a in alerts:
                        st = a.get("anomalystatus","")
                        if st == "object_missing":
                            cmd = {"type":"motor","value":"BACKWARD"}
                        elif st == "object_moved":
                            cmd = {"type":"motor","value":"FORWARD"}
                        elif st == "harmful_action":
                            cmd = {"type":"motor","value":"STOP"}
                        elif st == "bad_posture":
                            cmd = {"type":"servo","value":"90"}
                        else:
                            continue
                        handle_alert_command(cmd)
                    alert_counter += 1
                else:
                    print("[✓] Yeni alert yok.")
            else:
                print(f"[!] API hata: {resp.status_code}")
        except Exception as e:
            print(f"[ERR] API erişim hatası: {e}")
        time.sleep(30)

# ==== MANUEL KOMUT GİRİŞİ ====
def manual_command_sender():
    print("""
[Manual Komut Modu]
Komut formatı: CMD:MOTOR=FORWARD | CMD:MOTOR=STOP | CMD:SERVO=90
Çıkmak için: q
""")
    while True:
        cmd = input(">> ").strip()
        if cmd.lower() == "q":
            break
        if cmd.startswith("CMD:"):
            try:
                ser.write((cmd + "\n").encode())
                print(f"[Sent] {cmd}")
            except Exception as e:
                print(f"[!] Gönderilemedi: {e}")
        else:
            print("[!] Format: CMD:<TYPE>=<VALUE>")

# ==== ANA DÖNGÜ ====
def main_loop():
    last_a = last_p = 0
    while True:
        now = time.time()
        if now - last_a >= 5 and ser.in_waiting > 0:
            line = ser.readline().decode("utf-8").strip()
            if line.startswith("DATA:"):
                parsed = parse_arduino(line)
                fname = f"Arduino_{datetime.now():%Y%m%d_%H%M%S}.json"
                path  = get_pending_log_path(fname)
                write_json(parsed, path)
                print(f"[Arduino] Logged → {fname}")
            last_a = now
        if now - last_p >= 5:
            stats = get_system_stats()
            fname = "Pi5_Latest.json"
            path  = get_pending_log_path(fname)
            write_json(stats, path)
            print("[Pi5] Updated system stats.")
            last_p = now
        time.sleep(0.5)

# ==== BAŞLAT ====
ensure_dirs()
threading.Thread(target=photo_loop, daemon=True).start()
threading.Thread(target=retry_pending_loop, daemon=True).start()
threading.Thread(target=alert_listener, daemon=True).start()
threading.Thread(target=manual_command_sender, daemon=True).start()

try:
    main_loop()
except KeyboardInterrupt:
    print("Program stopped.")
