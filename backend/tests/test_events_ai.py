from __future__ import annotations
from fastapi.testclient import TestClient
from .test_auth import get_token


def test_event_triggers_ai_and_notify_log(client: TestClient):
    # user creates an event
    token = get_token(client, "user", "userpass")
    headers = {"Authorization": f"Bearer {token}"}

    # Create an event
    resp = client.post(
        "/events/",
        json={"event_type": "modify", "target_file_id": None, "target_folder_id": None},
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
