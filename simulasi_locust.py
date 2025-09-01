from locust import HttpUser, task, between, constant_pacing
import random

class UpdateLokasiUser(HttpUser):
    # wait_time = between(1, 2)  # Tunggu antar request (bisa disesuaikan)
    wait_time = constant_pacing(60)

    @task
    def update_lokasi(self):
        # Simulasi data random untuk pengujian
        lat = random.uniform(-6.5, -6.1)     # Sekitar Jakarta
        long = random.uniform(106.7, 107.0)
        nopol = random.choice(["B 1234 ABC", "B 5678 XYZ", "D 9876 ZYX"])

        payload = {
            "nopol": nopol,
            "lat": lat,
            "long": long
        }

        self.client.post("/update-lokasi", json=payload)