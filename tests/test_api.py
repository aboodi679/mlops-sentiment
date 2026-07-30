from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Mock the model before importing the app
with patch("app.model._model") as mock:
    mock.return_value = [{"label": "POSITIVE", "score": 0.9998}]
    from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_positive():
    with patch("app.model.predict") as mock_predict:
        mock_predict.return_value = {"label": "POSITIVE", "score": 0.9998}
        response = client.post("/predict", json={"text": "I love this!"})
        assert response.status_code == 200
        assert response.json()["label"] == "POSITIVE"

def test_predict_negative():
    with patch("app.model.predict") as mock_predict:
        mock_predict.return_value = {"label": "NEGATIVE", "score": 0.9987}
        response = client.post("/predict", json={"text": "This is terrible."})
        assert response.status_code == 200
        assert response.json()["label"] == "NEGATIVE"

def test_predict_empty_text():
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 400

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200