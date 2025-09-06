from locust import HttpUser, task, between, constant_pacing
import random
import csv
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

# Membaca plate_number 
def load_plate_numbers(filename="plate.csv"):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0] for row in reader if row]  # Hindari baris kosong

plate_numbers = load_plate_numbers()

class UpdateLokasiUser(HttpUser):
    # wait_time = between(1, 2)  # Tunggu antar request (bisa disesuaikan)
    wait_time = constant_pacing(60)
    token = os.getenv("TOKEN")
    if not token:
        raise RuntimeError("TOKEN environment variable is missing!")

    @task
    def update_lokasi(self):
        # Simulasi data random untuk pengujian
        lat = random.uniform(-8.5, -6.1)     # Sekitar Jakarta
        long = random.uniform(105.7, 114.0)

        payload = {
            "gps_imei": "No IMEI GPS",
            "gps_vendor": "Brand or Vendor GPS",
            "gps_network": "2G / 4G",
            "plate_number": random.choice(plate_numbers),
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
        self.client.post("/vehicle/karlo-update2/", json=payload, headers=headers)
        # self.client.get("/patients/", headers=headers)
        # Debugging print
        # print(f"POST to /vehicle/karlo-update/")
        # print(f"Headers: {headers}")
        # print(f"Payload: {json.dumps(payload)}")

        # with self.client.post("/vehicle/karlo-update/", json=payload, headers=headers, catch_response=True) as response:
        #     if response.status_code != 200:
        #         response.failure(f"Unexpected status code: {response.status_code} - {response.text}")
        #     else:
        #         response.success()