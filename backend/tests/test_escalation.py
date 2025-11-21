from __future__ import annotations
import time
from fastapi.testclient import TestClient
from .test_auth import get_token
from app.config import settings


def test_escalation_runs_via_background_tasks(client: TestClient):
    # Force zero delays for fast test
    settings.escalation_high_delay_seconds = 0
    settings.escalation_critical_delay_seconds = 0

    # Create a High severity rule so events escalate
    admin_token = get_token(client, "admin", "adminpass")
    aheaders = {"Authorization": f"Bearer {admin_token}"}
    r = client.post(
        "/ai-rules/",
        json={
            "rule_name": "force-high",
            "description": "force high severity for all events",
            "severity_level": "High",
            "action_type": "notify",
            "adaptive_flag": False,
        },
        headers=aheaders,
    )
    assert r.status_code == 200, r.text

    # User triggers an event
    user_token = get_token(client, "user", "userpass")
    uheaders = {"Authorization": f"Bearer {user_token}"}
    
    # Create a folder first to use in the event
    folder_resp = client.post("/folders/", json={"name": "test_folder", "path": "/tmp/test_folder"}, headers=uheaders)
    assert folder_resp.status_code == 200, folder_resp.text
    folder = folder_resp.json()
    
    eresp = client.post(
        "/events/",
        json={"event_type": "modify", "target_folder_id": folder["id"]},
        headers=uheaders,
    )
    assert eresp.status_code == 200, eresp.text

    # Poll logs briefly until ESCALATE appears (BackgroundTasks executes after response)
    found = False
    for _ in range(10):
        logs = client.get("/logs/", headers=aheaders)
        assert logs.status_code == 200
        types = [entry["log_type"] for entry in logs.json()]
        if "ESCALATE" in types:
            found = True
            break
        time.sleep(0.05)

    assert found, "Expected ESCALATE log to be created by background task"
