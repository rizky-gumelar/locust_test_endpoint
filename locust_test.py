from locust import HttpUser, task, between

class PingUser(HttpUser):
    # Waktu tunggu antar request (optional), bisa diubah sesuai kebutuhan
    wait_time = between(1, 2)

    @task
    def ping_endpoint(self):
        self.client.get("/ping")
