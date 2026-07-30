# MLOps Sentiment Analysis Pipeline

A production-grade MLOps pipeline deploying a sentiment analysis model on Kubernetes.

## Architecture

- **Model**: DistilBERT sentiment classifier (HuggingFace)
- **API**: FastAPI with Prometheus metrics
- **Container**: Docker (model weights baked in at build time)
- **Infrastructure**: AWS EKS via Terraform
- **Packaging**: Helm chart with HPA and health probes
- **CI/CD**: GitHub Actions with OIDC (no long-lived AWS keys)
- **Monitoring**: Prometheus + Grafana (inference latency, request rate, error rate)

## Project Structure
mlops-sentiment/
├── app/ # FastAPI application
│ ├── main.py # API endpoints + Prometheus metrics
│ └── model.py # HuggingFace sentiment model
├── tests/ # Pytest test suite
├── helm/sentiment-api/ # Helm chart
├── terraform/ # EKS + ECR + OIDC infrastructure
└── .github/workflows/ # CI/CD pipeline
## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/predict` | POST | Run sentiment inference |
| `/metrics` | GET | Prometheus metrics |

## Usage

```bash
curl -X POST http://<LOAD_BALANCER_URL>/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This project is amazing!"}'

# Response
{"label": "POSITIVE", "score": 0.9998}
```

## Infrastructure

Provisioned with Terraform:
- VPC with public/private subnets across 2 AZs
- EKS cluster (Kubernetes 1.32) with managed node group
- ECR repository for Docker images
- IAM OIDC provider for GitHub Actions (no static credentials)

## Monitoring

After deployment, access Grafana dashboard tracking:
- Inference requests per second
- p95 inference latency
- Error rate