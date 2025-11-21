from __future__ import annotations
from fastapi.testclient import TestClient

from .test_auth import get_token

def test_folders_files_crud_and_audit_logs(client: TestClient):
    token = get_token(client, "user", "userpass")
    headers = {"Authorization": f"Bearer {token}"}

    # Create folder
    resp = client.post("/folders/", json={"name": "docs", "path": "/tmp/docs"}, headers=headers)
    assert resp.status_code == 200, resp.text
    folder = resp.json()

    # Create file in folder
    resp = client.post("/files/", json={"name": "readme.txt", "path": "/tmp/docs/readme.txt", "folder_id": folder["id"]}, headers=headers)
    assert resp.status_code == 200, resp.text
    file_obj = resp.json()

    # Delete file
    resp = client.delete(f"/files/{file_obj['id']}", headers=headers)
    assert resp.status_code == 200, resp.text

    # Delete folder
    resp = client.delete(f"/folders/{folder['id']}", headers=headers)
    assert resp.status_code == 200, resp.text

    # Logs should contain audit records visible to user (related_event_id None)
    logs = client.get("/logs/", headers=headers)
    assert logs.status_code == 200, logs.text
    messages = [entry["message"] for entry in logs.json()]
    assert any("FOLDER_CREATE" in m for m in messages)
    assert any("FILE_CREATE" in m for m in messages)
    assert any("FILE_DELETE" in m for m in messages)
    assert any("FOLDER_DELETE" in m for m in messages)
