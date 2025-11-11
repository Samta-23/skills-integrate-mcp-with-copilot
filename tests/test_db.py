from fastapi.testclient import TestClient
import os

from src.app import app


client = TestClient(app)


def test_get_activities_returns_seeded_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # some seeded activity names should exist
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_prevent_duplicate():
    email = "tester@example.com"
    activity = "Chess Club"
    # ensure not signed up yet
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    # duplicate signup should fail
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400


def test_unregister():
    email = "tester2@example.com"
    activity = "Programming Class"
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    # now unregister
    resp2 = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp2.status_code == 200
