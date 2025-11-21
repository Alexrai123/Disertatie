from __future__ import annotations
from fastapi.testclient import TestClient
from .test_auth import get_token


def test_logs_visibility_and_chatbot_endpoints(client: TestClient):
    # user creates an event to generate logs
    user_token = get_token(client, "user", "userpass")
    uheaders = {"Authorization": f"Bearer {user_token}"}
    client.post(
        "/events/",
        json={"event_type": "modify", "target_file_id": None, "target_folder_id": None},
        headers=uheaders,
    )

    # user can see own logs (NOTIFY may be unrelated to event; still should see some logs)
    resp = client.get("/logs/", headers=uheaders)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # admin sees all logs
    admin_token = get_token(client, "admin", "adminpass")
    aheaders = {"Authorization": f"Bearer {admin_token}"}
    admin_logs = client.get("/logs/", headers=aheaders)
    assert admin_logs.status_code == 200
    assert len(admin_logs.json()) >= len(resp.json())

    # chatbot endpoints (admin-only)
    sm = client.get("/chatbot/summary", headers=aheaders)
    assert sm.status_code == 200
    q = client.get("/chatbot/query", headers=aheaders)
    assert q.status_code == 200

    # non-admin forbidden
    sm2 = client.get("/chatbot/summary", headers=uheaders)
    assert sm2.status_code in (401, 403)
