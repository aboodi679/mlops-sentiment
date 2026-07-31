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

<img width="539" height="34" alt="image" src="https://github.com/user-attachments/assets/b98df257-0ef2-495f-b07a-1a6067a195e8" />


---

## CI/CD Pipeline

Three-stage GitHub Actions pipeline triggered on push to `main`:

1. **Test** — runs pytest with mocked DistilBERT
2. **Build & Push** — builds Docker image, pushes to ECR
3. **Deploy** — Helm upgrade to EKS cluster

Authentication uses GitHub OIDC (`AssumeRoleWithWebIdentity`) — no AWS access keys stored in GitHub secrets.

---

<img width="1349" height="333" alt="image" src="https://github.com/user-attachments/assets/6cc566dc-dbc9-413d-8c60-80f73dcfeb02" />


---

## Kubernetes Deployment

```bash
kubectl get pods
```

---

<img width="775" height="83" alt="image" src="https://github.com/user-attachments/assets/2bc29241-7c58-417e-84b3-aec9f5a5571d" />


---

```bash
kubectl get svc sentiment-api
```

---

<img width="1128" height="138" alt="image" src="https://github.com/user-attachments/assets/c2a21f04-7cb4-4f0a-9907-6a644b053995" />


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

<img width="1900" height="471" alt="image" src="https://github.com/user-attachments/assets/3b042bec-66ea-46a0-94bf-81db13635813" />


---

<img width="1455" height="694" alt="image" src="https://github.com/user-attachments/assets/20ab3986-fe8f-4ec4-ab77-e8604b119c6f" />


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
AWS Account:  ****
Region:       us-east-1
EKS Cluster:  mlops-cluster
GitHub Repo:  aboodi679/mlops-sentiment
```
