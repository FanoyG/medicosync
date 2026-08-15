from locust import HttpUser, task, between
import uuid

class AuthUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Runs ONCE per simulated user — registers a unique account first."""
        self.email = f"loadtest_{uuid.uuid4().hex[:8]}@medicosync.com"
        self.password = "LoadTest123!@"

        self.client.post("/auth/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": "Load Test Doctor",
            "role": "doctor",
            "gender": "male",
            "phone": {"country_code": "+91", "number": "9876543210"}
        })

    @task(8)
    def login_correct(self):
        """Most traffic: normal successful logins."""
        self.client.post("/auth/login", json={
            "email": self.email,
            "password": self.password
        })

    @task(1)
    def login_wrong_password(self):
        """Occasional wrong password — exercises the lockout path under load."""
        self.client.post("/auth/login", json={
            "email": self.email,
            "password": "WrongPassword999!"
        })