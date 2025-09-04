from locust import HttpUser, task, between, constant_pacing
import random
import csv
import json
import threading
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

# Membaca plate_number 
def load_plate_numbers(filename="plate.csv"):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0] for row in reader if row]  # Hindari baris kosong

class UpdateLokasiUser(HttpUser):
    # wait_time = between(1, 2)  # Tunggu antar request (bisa disesuaikan)
    wait_time = constant_pacing(60)

    # Shared among all users
    plate_numbers = load_plate_numbers()
    plate_lock = threading.Lock()
    available_plate_numbers = plate_numbers.copy()
    token = os.getenv("TOKEN")
    if not token:
        raise RuntimeError("TOKEN environment variable is missing!")

    def on_start(self):
        # Ambil satu plate secara unik per user
        with self.plate_lock:
            if self.available_plate_numbers:
                self.plate_number = self.available_plate_numbers.pop()
            else:
                self.plate_number = random.choice(self.plate_numbers)  # fallback jika habis
                print(f"[WARNING] No more unique plates. Reusing: {self.plate_number}")


    @task
    def update_lokasi(self):
        # Simulasi data random untuk pengujian
        lat = random.uniform(-5.8, -7.8)     # Sekitar Jakarta
        long = random.uniform(106.7, 107.0)
        # lat = random.uniform(-9.0, -5.8)     # Lintang Selatan (negatif)
        # long = random.uniform(105.5, 114.0)  # Bujur Timur

        payload = {
            "gps_imei": "No IMEI GPS",
            "gps_vendor": "Brand or Vendor GPS",
            "gps_network": "2G / 4G",
            "plate_number": self.plate_number,
            "latitude": lat,
            "longitude": long,
            "altitude": 0,
            "bearing": 0,
            "speed": 30,
            "battery": 50,
            "lastUpdated": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        }
        headers = {
            "Authorization": f"Bearer {self.token}",  # token asli dari curl
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # print(f"Sending update for plate: {payload['plate_number']}")
        self.client.post("/vehicle/karlo-update/", json=payload, headers=headers)
        print(f"[INFO] User {self.environment.runner.user_count} using plate: {self.plate_number}")
        # self.client.get("/patients/", headers=headers)
