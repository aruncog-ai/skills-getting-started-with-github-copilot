from fastapi.testclient import TestClient
import copy
import pytest

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep copy of the initial activities and restore after each test
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(orig)


def test_get_activities():
    r = client.get('/activities')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert 'Chess Club' in data


def test_signup_and_reflect():
    activity = 'Drama Club'
    email = 'tester@example.com'

    # Ensure precondition: email not already in participants
    assert email not in activities[activity]['participants']

    r = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert r.status_code == 200
    assert 'Signed up' in r.json().get('message', '')

    # After signup, activity should include the new participant
    r2 = client.get('/activities')
    participants = r2.json()[activity]['participants']
    assert email in participants


def test_remove_participant():
    activity = 'Chess Club'
    email = 'michael@mergington.edu'

    # Ensure participant exists initially
    assert email in activities[activity]['participants']

    r = client.delete(f"/activities/{activity}/participant", params={'email': email})
    assert r.status_code == 200
    assert 'Unregistered' in r.json().get('message', '')

    # After removal, participant should be gone
    r2 = client.get('/activities')
    participants = r2.json()[activity]['participants']
    assert email not in participants
