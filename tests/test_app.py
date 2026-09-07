import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_homepage_render():
    response = client.get("/")
    assert response.status_code == 200
    assert "ScriptDoctor AI" in response.text
