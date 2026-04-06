import uuid
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_register():
    email = f"test_{uuid.uuid4()}@example.com"
    
    response = client.post("/register", params={
        "email": email,
        "password": "12345"
    })
    
    assert response.status_code == 200