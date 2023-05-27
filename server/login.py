from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def login():
    response = client.post("/login", data={"username": "demo", "password": "secret"},
                           headers={"content-type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert "token_type" in response_data
    assert response_data["token_type"] == "bearer"
    return response_data["token_type"], response_data["access_token"], response_data["refresh_token"]

type, access, refresh = login()
