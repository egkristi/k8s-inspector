# k8s-inspector 2.0 🐦‍⬛

> **The Intelligent Kubernetes Inspector**  
> Not just monitoring — *understanding*. Not just alerts — *answers*. Not just problems — *solutions*.

[![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://opensource.org/licenses/AGPL-3.0)
[![GitHub stars](https://img.shields.io/github/stars/egkristi/k8s-inspector.svg)](https://github.com/egkristi/k8s-inspector/stargazers)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-brightgreen)](https://egkristi.github.io/k8s-inspector/)

📚 **[Read the full documentation here](https://egkristi.github.io/k8s-inspector/)**

---

## 🚀 Quick Start

### One-Command Deploy (Helm)

```bash
helm repo add k8s-inspector https://charts.k8s-inspector.dev
helm install k8s-inspector k8s-inspector/k8s-inspector --namespace k8s-inspector --create-namespace
kubectl port-forward svc/k8s-inspector-frontend 3000:80 -n k8s-inspector
```

### Local Development (Docker Compose)

```bash
git clone https://github.com/egkristi/k8s-inspector.git
cd k8s-inspector
docker-compose -f deploy/local/docker-compose.yml up -d
```

Access:
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## ✨ Killer Features

### 🧠 AI-Powered Root Cause Analysis
Not just "Pod is crashing" — but *why*, and *how to fix it*.

### 💰 Intelligent Cost Optimization
Real savings recommendations, not just charts.

### 🔮 Predictive Failure Detection
Fix problems before they happen with ML-powered anomaly detection.

### 🔐 Security Compliance
CIS benchmarks, NSA/CISA guidelines — with one-click remediation.

### 🌐 Multi-Cluster Federated View
One dashboard, unlimited clusters.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              k8s-inspector 2.0                  │
├─────────────────────────────────────────────────┤
│  Next.js 14 Dashboard (WebSocket Real-time)    │
│         ↓                                        │
│  FastAPI Backend (Async Python)                │
│         ↓                                        │
│  PostgreSQL + TimescaleDB (Metrics)            │
│  Redis (Cache + Pub/Sub)                       │
│         ↓                                        │
│  Kubernetes Clusters (N)                       │
└─────────────────────────────────────────────────┘
```

---

## 📊 What Gets Inspected?

**Cluster Health:** Control plane, etcd, nodes, operators, certificates  
**Workloads:** Pods, deployments, StatefulSets, restarts, resources  
**Cost:** Compute, storage, network — with optimization tips  
**Security:** CIS benchmarks, pod security, network policies  
**Performance:** Anomaly detection, predictions, capacity planning  

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14 + Tailwind + shadcn/ui |
| Backend | FastAPI (Python async) |
| Database | PostgreSQL + TimescaleDB |
| Cache | Redis |
| ML | scikit-learn + PyTorch |
| Deploy | Helm + Docker |

---

## 📈 Roadmap

- [x] Core platform architecture
- [x] FastAPI backend skeleton
- [x] Database models
- [x] Docker Compose
- [x] Helm chart
- [ ] Next.js dashboard
- [ ] Cost analyzer engine
- [ ] Security analyzer (CIS)
- [ ] ML anomaly detection
- [ ] Auto-remediation playbooks

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

k8s-inspector uses a **dual-license model**:
- **Open Source Core:** GNU AGPLv3
- **Enterprise Features:** Commercial License

See [LICENSING.md](LICENSING.md) for full details, features, and terms.

---

<div align="center">

**Made with ❤️ by [@egkristi](https://github.com/egkristi)**

⭐ Star this repo if you find it useful!

</div>
