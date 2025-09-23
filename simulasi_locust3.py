from locust import HttpUser
import csv
import threading
import random
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
    tasks = [] 
    # wait_time = constant_pacing(60)  # Tidak perlu jika hanya 1x jalan
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
                self.plate_number = random.choice(self.plate_numbers)
                print(f"[WARNING] No more unique plates. Reusing: {self.plate_number}")

        # Kirim 1x POST langsung di on_start
        self.update_lokasi()

    def update_lokasi(self):
        city_coords = {
            "semarang": {
                "lat": (-7.10, -6.95),
                "long": (110.30, 110.50)
            },
            "bandung": {
                "lat": (-7.05, -6.95),
                "long": (107.55, 107.65)
            },
            "surabaya": {
                "lat": (-7.35, -7.25),
                "long": (112.70, 112.80)
            }
        }

        city = random.choice(list(city_coords.keys()))
        lat = random.uniform(*city_coords[city]["lat"])
        long = random.uniform(*city_coords[city]["long"])

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
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.client.post("/vehicle/karlo-update2/", json=payload, headers=headers)
        print(f"[INFO] User {self.environment.runner.user_count} using plate: {self.plate_number} in {city.title()}")
