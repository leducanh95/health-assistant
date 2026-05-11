import pytest


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


class TestSignup:
    def test_success_returns_201_with_token(self, client):
        resp = client.post("/api/auth/signup", json={
            "email": "new@example.com",
            "password": "securepassword123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)

    def test_duplicate_email_returns_409(self, client):
        payload = {"email": "dupe@example.com", "password": "password1234"}
        client.post("/api/auth/signup", json=payload)
        resp = client.post("/api/auth/signup", json=payload)
        assert resp.status_code == 409

    def test_short_password_returns_422(self, client):
        # min_length=8 in UserCreate schema
        resp = client.post("/api/auth/signup", json={
            "email": "short@example.com",
            "password": "short",
        })
        assert resp.status_code == 422

    def test_invalid_email_returns_422(self, client):
        resp = client.post("/api/auth/signup", json={
            "email": "not-an-email",
            "password": "validpassword123",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_valid_credentials_returns_token(self, client):
        creds = {"email": "login@example.com", "password": "password1234"}
        client.post("/api/auth/signup", json=creds)
        resp = client.post("/api/auth/login", json=creds)
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_wrong_password_returns_401(self, client):
        client.post("/api/auth/signup", json={
            "email": "wrongpw@example.com", "password": "correctpassword1",
        })
        resp = client.post("/api/auth/login", json={
            "email": "wrongpw@example.com", "password": "wrongpassword99",
        })
        assert resp.status_code == 401

    def test_nonexistent_user_returns_401(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "ghost@example.com", "password": "anypassword123",
        })
        assert resp.status_code == 401


class TestMe:
    def test_authenticated_returns_user_data(self, client):
        creds = {"email": "me@example.com", "password": "password5678"}
        signup_resp = client.post("/api/auth/signup", json=creds)
        token = signup_resp.json()["access_token"]
        resp = client.get("/api/auth/me",
                          headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == creds["email"]
        assert "id" in data
        assert "created_at" in data

    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, client):
        resp = client.get("/api/auth/me",
                          headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401
