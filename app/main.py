from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
from pydantic import BaseModel
import time
from app.model import predict

app = FastAPI(title="Sentiment API", version="1.0.0")

# Prometheus metrics
REQUEST_COUNT = Counter(
    "inference_requests_total",
    "Total inference requests",
    ["status"]
)
LATENCY = Histogram(
    "inference_latency_seconds",
    "Inference latency in seconds"
)

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    label: str
    score: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def run_predict(payload: PredictRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    start = time.time()
    try:
        result = predict(payload.text)
        REQUEST_COUNT.labels(status="success").inc()
        LATENCY.observe(time.time() - start)
        return result
    except Exception as e:
        REQUEST_COUNT.labels(status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")