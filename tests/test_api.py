from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_positive():
    response = client.post("/predict", json={"text": "I love this product!"})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "POSITIVE"
    assert data["score"] > 0.9

def test_predict_negative():
    response = client.post("/predict", json={"text": "This is terrible."})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "NEGATIVE"

def test_predict_empty_text():
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 400

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"inference_requests_total" in response.content