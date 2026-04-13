# Getting Started

## Quick Start (Local Development)

The easiest way to try out k8s-inspector 2.0 is using Docker Compose. This will spin up the FastAPI backend, Next.js dashboard, PostgreSQL, and Redis.

```bash
git clone https://github.com/egkristi/k8s-inspector.git
cd k8s-inspector

# Start all services
docker-compose -f deploy/local/docker-compose.yml up -d
```

### Accessing the Services
* **Dashboard:** [http://localhost:3000](http://localhost:3000)
* **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Production Deployment (Helm)

For production, deploy k8s-inspector directly into your Kubernetes cluster using our Helm chart.

```bash
# Add the Helm repository
helm repo add k8s-inspector https://charts.k8s-inspector.dev
helm repo update

# Install the chart
helm install k8s-inspector k8s-inspector/k8s-inspector \
  --namespace k8s-inspector \
  --create-namespace
```

### Helm Configuration

You can customize the installation by providing a `values.yaml` file:

```yaml
frontend:
  ingress:
    enabled: true
    hosts:
      - host: dashboard.k8s.yourdomain.com
        paths:
          - path: /
            pathType: Prefix

ml:
  anomalyDetection:
    enabled: true
```
