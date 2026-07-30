FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download model weights at build time
RUN python -c "from transformers import pipeline; \
    pipeline('sentiment-analysis', \
    model='distilbert-base-uncased-finetuned-sst-2-english')"

# Copy app code
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]