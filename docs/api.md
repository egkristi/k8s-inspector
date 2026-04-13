# Backend API Reference

k8s-inspector 2.0 is powered by a high-performance Python **FastAPI** backend that provides the core logic for the Next.js Dashboard.

This page provides an overview of the REST API and WebSocket capabilities.

## OpenAPI Documentation

FastAPI automatically generates interactive OpenAPI (Swagger) documentation. When the backend is running locally, you can access it at:
[http://localhost:8000/docs](http://localhost:8000/docs)

## Key Endpoints

### 1. `GET /api/v2/clusters`
Returns a list of all registered Kubernetes clusters and their summary statistics.
- **Response:**
  ```json
  [
    {
      "id": 1,
      "name": "prod-eu",
      "cluster_type": "kubernetes",
      "is_active": true,
      "health_score": 98.7,
      "node_count": 12,
      "pod_count": 340,
      "monthly_cost_estimate": 4200.0,
      "currency": "USD"
    }
  ]
  ```

### 2. `POST /api/v2/clusters`
Registers a new Kubernetes cluster with the inspector.
- **Body:**
  ```json
  {
    "name": "staging",
    "cluster_type": "kubernetes",
    "kubeconfig_secret": "secret_name_in_k8s"
  }
  ```

### 3. `GET /api/v2/insights`
Retrieves generated insights from the Cost, Security, and ML Analyzers.
- **Filters:** `?cluster_id=1&severity=critical&category=security`
- **Response:**
  ```json
  [
    {
      "id": 42,
      "cluster_id": 1,
      "category": "security",
      "severity": "critical",
      "title": "Enforce Pod Security Standards",
      "recommendation": "Found 12 pod security violations (root execution).",
      "auto_fix_available": true
    }
  ]
  ```

## WebSocket Real-Time Telemetry

The Next.js Dashboard communicates with the FastAPI backend over WebSockets to provide a live, real-time view of cluster anomalies, events, and metrics.

### `ws://localhost:8000/ws/cluster/{cluster_id}`
Connect to this endpoint to receive live updates.

**Incoming Messages (from Backend):**
- Real-time metrics
- Instant anomaly detections
- Playbook execution logs

**Outgoing Messages (from Dashboard):**
- Keep-alive `ping`
- Trigger auto-remediation (Playbooks)
