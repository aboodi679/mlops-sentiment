# MLOps Sentiment Pipeline

A production-grade MLOps pipeline serving a DistilBERT sentiment classifier on AWS EKS, with full CI/CD, Helm deployment, and Prometheus/Grafana observability.

## Architecture

```
GitHub Actions (CI/CD)
    │
    ├── Test → Build → Push to ECR
    │
    └── Helm Deploy → EKS Cluster
                          │
                    ┌─────┴─────┐
                    Pod 1      Pod 2
                 (DistilBERT) (DistilBERT)
                    └─────┬─────┘
                          │
                    LoadBalancer
                          │
                    /predict /health /metrics
                          │
                    Prometheus → Grafana
```

## Stack

| Layer | Technology |
|-------|-----------|
| Model | DistilBERT (HuggingFace) |
| API | FastAPI |
| Container | Docker → AWS ECR |
| Orchestration | Kubernetes (AWS EKS 1.32) |
| IaC | Terraform |
| CI/CD | GitHub Actions + OIDC |
| Package Manager | Helm |
| Observability | Prometheus + Grafana |

## Infrastructure

- VPC with public/private subnets across 2 AZs
- EKS cluster with 2x t3.small nodes
- ECR repository for Docker images
- GitHub Actions OIDC — keyless authentication (no static credentials)
- All resources in `us-east-1`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Run sentiment inference |
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |

### Example

```bash
curl -X POST http://<EXTERNAL-IP>/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This MLOps pipeline is working perfectly!"}'
```

Response:
```json
{"label": "POSITIVE", "score": 0.9993}
```

---

**[SCREENSHOT 3 HERE — terminal showing the predict response]**

---

## CI/CD Pipeline

Three-stage GitHub Actions pipeline triggered on push to `main`:

1. **Test** — runs pytest with mocked DistilBERT
2. **Build & Push** — builds Docker image, pushes to ECR
3. **Deploy** — Helm upgrade to EKS cluster

Authentication uses GitHub OIDC (`AssumeRoleWithWebIdentity`) — no AWS access keys stored in GitHub secrets.

---

**[SCREENSHOT 1 HERE — GitHub Actions showing all 3 jobs green]**

---

## Kubernetes Deployment

```bash
kubectl get pods
```

---

**[SCREENSHOT HERE — kubectl get pods showing 2/2 Running]**

---

```bash
kubectl get svc sentiment-api
```

---

**[SCREENSHOT HERE — kubectl get svc showing LoadBalancer external IP]**

---

Features:
- 2 replicas with HPA (scales 2→10 based on CPU)
- Liveness and readiness probes on `/health`
- Resource limits: 500m CPU, 1Gi memory per pod

## Observability

Prometheus scrapes `/metrics` from both pods every 15s via ServiceMonitor.

Custom metrics exposed:
- `inference_requests_total` — total predictions by status (success/error)
- `inference_latency_seconds` — DistilBERT inference latency histogram

---

**[SCREENSHOT 4 HERE — Prometheus targets showing sentiment-api 2/2 UP]**

---

**[SCREENSHOT 5 HERE — Grafana showing inference_latency_seconds metrics]**

---

## Notable Engineering Decisions

**OIDC Keyless Auth** — GitHub Actions authenticates to AWS via OIDC instead of static credentials. Debugging this revealed that GitHub's `sub` claim uses numeric IDs (`user@214363717/repo@1317687475`) rather than slugs — only visible via CloudTrail. Trust policy must match the exact numeric format.

**Model weights baked into Docker image** — DistilBERT weights downloaded at build time, eliminating cold-start latency from model loading at runtime.

**ServiceMonitor namespace cross-linking** — Prometheus runs in `monitoring` namespace, app in `default`. Required patching `serviceMonitorNamespaceSelector: {}` on the Prometheus CR to scrape across namespaces.

## Project Structure

```
mlops-sentiment/
├── app/
│   ├── main.py          # FastAPI app + Prometheus metrics
│   ├── model.py         # DistilBERT inference
│   └── __init__.py
├── tests/
│   └── test_api.py      # Mocked unit tests
├── helm/
│   └── sentiment-api/   # Helm chart with HPA + ServiceMonitor
├── .github/
│   └── workflows/
│       ├── deploy.yml       # CI/CD pipeline
│       └── monitoring.yml   # One-time monitoring install
├── Dockerfile
├── requirements.txt
└── README.md
```

## Local Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Infrastructure Setup

```bash
cd terraform/
terraform init
terraform apply
```

## Key Values

```
AWS Account:  026243800492
Region:       us-east-1
EKS Cluster:  mlops-cluster
ECR URL:      026243800492.dkr.ecr.us-east-1.amazonaws.com/sentiment-api
GitHub Repo:  aboodi679/mlops-sentiment
```