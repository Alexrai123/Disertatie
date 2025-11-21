from __future__ import annotations
from fastapi.testclient import TestClient

def get_token(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/auth/token", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]

def test_login_and_me(client: TestClient):
    token = get_token(client, "admin", "adminpass")
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    data = me.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"
