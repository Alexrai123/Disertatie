from __future__ import annotations
from fastapi.testclient import TestClient
from .test_auth import get_token


def test_ai_rules_crud_admin_only_and_feedback(client: TestClient):
    admin_token = get_token(client, "admin", "adminpass")
    aheaders = {"Authorization": f"Bearer {admin_token}"}

    # Create rule
    payload = {
        "rule_name": "High Modify",
        "description": "test",
        "severity_level": "High",
        "action_type": "notify",
        "adaptive_flag": True,
    }
    resp = client.post("/ai-rules/", json=payload, headers=aheaders)
    assert resp.status_code == 200, resp.text
    rule = resp.json()

    # Update rule
    payload["description"] = "updated"
    resp = client.put(f"/ai-rules/{rule['id']}", json=payload, headers=aheaders)
    assert resp.status_code == 200, resp.text

    # Non-admin cannot list rules
    user_token = get_token(client, "user", "userpass")
    uheaders = {"Authorization": f"Bearer {user_token}"}
    resp = client.get("/ai-rules/", headers=uheaders)
    assert resp.status_code in (401, 403)

    # Create an event as user, then give admin feedback
    resp = client.post(
        "/events/",
        json={"event_type": "modify", "target_file_id": None, "target_folder_id": None},
        headers=uheaders,
    )
    assert resp.status_code == 200
    event = resp.json()

    fb_payload = {"event_id": event["id"], "feedback_type": "approve", "comment": "ok", "rule_id": rule["id"]}
    resp = client.post("/feedback/", json=fb_payload, headers=aheaders)
    assert resp.status_code == 200, resp.text

    # Cleanup rule
    resp = client.delete(f"/ai-rules/{rule['id']}", headers=aheaders)
    assert resp.status_code == 200
