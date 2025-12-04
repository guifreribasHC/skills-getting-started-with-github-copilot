from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)

TEST_EMAIL = "pytest.user@example.com"
TEST_ACTIVITY = "Chess Club"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert TEST_ACTIVITY in data


def test_signup_and_unregister_flow():
    # Ensure the test email is not present in any activity before starting
    for act in app_module.activities.values():
        if TEST_EMAIL in act["participants"]:
            act["participants"].remove(TEST_EMAIL)

    # Signup
    resp = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Verify backend state updated
    assert TEST_EMAIL in app_module.activities[TEST_ACTIVITY]["participants"]

    # Try signing up again for same (should fail because already signed up for an activity)
    resp2 = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp2.status_code == 400

    # Unregister
    resp_del = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email={TEST_EMAIL}")
    assert resp_del.status_code == 200
    body_del = resp_del.json()
    assert "Unregistered" in body_del.get("message", "")

    # Verify removed
    assert TEST_EMAIL not in app_module.activities[TEST_ACTIVITY]["participants"]


def test_unregister_nonexistent_returns_404():
    # pick an email that is almost certainly not registered
    email = "not-registered@example.com"
    # ensure it's not in activity
    if email in app_module.activities[TEST_ACTIVITY]["participants"]:
        app_module.activities[TEST_ACTIVITY]["participants"].remove(email)

    resp = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email={email}")
    assert resp.status_code == 404
    data = resp.json()
    assert data.get("detail") == "Participant not found in activity"
