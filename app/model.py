from transformers import pipeline

# Load model once at startup
_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def predict(text: str) -> dict:
    result = _model(text)[0]
    return {
        "label": result["label"],
        "score": round(result["score"], 4)
    }