from locust import HttpUser, task, between

class AuthenticatedUser(HttpUser):
    wait_time = between(1, 3)  # Atur sesuai kebutuhan beban

    def on_start(self):
        # Login ke endpoint /auth/login
        login_payload = {
            "username": "admin",       # Ganti sesuai kebutuhan
            "password": "1234"         # Ganti sesuai kebutuhan
        }
        response = self.client.post("/auth/login", json=login_payload)

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            token_type = data.get("token_type", "bearer")
            self.auth_headers = {
                "Authorization": f"{token_type.capitalize()} {access_token}"
            }
        else:
            self.auth_headers = {}
            print(f"[Login Failed] {response.status_code}: {response.text}")

    @task
    def stress_protected_endpoint(self):
        if not self.auth_headers:
            return  # Lewati jika login gagal

        self.client.get("/patients/", headers=self.auth_headers)
