from __future__ import annotations
from fastapi.testclient import TestClient
from .test_auth import get_token


def test_event_triggers_ai_and_notify_log(client: TestClient):
    # user creates an event
    token = get_token(client, "user", "userpass")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a folder first to use in the event
    folder_resp = client.post("/folders/", json={"name": "test_folder", "path": "/tmp/test_folder"}, headers=headers)
    assert folder_resp.status_code == 200, folder_resp.text
    folder = folder_resp.json()

    # Create an event
    resp = client.post(
        "/events/",
        json={"event_type": "modify", "target_folder_id": folder["id"]},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text

    # Fetch logs as admin to see AI_DECISION and NOTIFY entries (user can also see NOTIFY with None related_event)
    admin_token = get_token(client, "admin", "adminpass")
    aheaders = {"Authorization": f"Bearer {admin_token}"}
    logs = client.get("/logs/", headers=aheaders)
    assert logs.status_code == 200
    types = [entry["log_type"] for entry in logs.json()]
    assert "AI_DECISION" in types
    assert "NOTIFY" in types
