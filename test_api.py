import requests
import pytest

BASE_URL = "http://localhost:8000"

@pytest.mark.parametrize("test_case", [
    {
        "test_name": "Create User with Valid Data",
        "payload": {"name": "John Doe", "email": "johndoe@example.com"},
        "expected_status": 200
    },
    {
        "test_name": "Create User without Name",
        "payload": {"email": "johndoe@example.com"},
        "expected_status": 422
    },
    {
        "test_name": "Create User with Invalid Email",
        "payload": {"name": "John Doe", "email": "invalid-email"},
        "expected_status": 422
    }
])
def test_create_user(test_case):
    response = requests.post(BASE_URL + "/users", json=test_case["payload"])
    assert response.status_code == test_case["expected_status"]