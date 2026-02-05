import copy
import sys
from pathlib import Path

from fastapi.testclient import TestClient

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.append(str(SRC_DIR))

import app as app_module

client = TestClient(app_module.app)


def restore_activities():
    return copy.deepcopy(app_module.activities)


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Soccer Team" in data
    assert "participants" in data["Soccer Team"]


def test_signup_adds_participant_and_prevents_duplicate():
    original = restore_activities()
    try:
        activity = "Chess Club"
        email = "test.student@mergington.edu"

        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        assert signup_response.status_code == 200
        assert email in app_module.activities[activity]["participants"]

        duplicate_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        assert duplicate_response.status_code == 400
    finally:
        app_module.activities = original


def test_unregister_participant_removes_entry():
    original = restore_activities()
    try:
        activity = "Drama Club"
        participant = app_module.activities[activity]["participants"][0]

        delete_response = client.delete(
            f"/activities/{activity}/participants",
            params={"participant": participant},
        )

        assert delete_response.status_code == 200
        assert participant not in app_module.activities[activity]["participants"]
    finally:
        app_module.activities = original
