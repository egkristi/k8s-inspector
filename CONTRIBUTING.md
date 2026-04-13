# Contributing to k8s-inspector 2.0 🐦‍⬛

First off, thank you for considering contributing to k8s-inspector! It's people like you that make k8s-inspector such a great tool for the Kubernetes community.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. We expect all contributors to maintain a respectful and welcoming environment.

## Getting Started Locally

The easiest way to get started is by using our Docker Compose environment, which spins up the backend, frontend, PostgreSQL (with TimescaleDB), and Redis.

### Prerequisites
* Docker and Docker Compose
* Git
* Node.js (v20+)
* Python (3.11+)

### Local Development Setup

1. **Fork and Clone:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/k8s-inspector.git
   cd k8s-inspector
   ```

2. **Start the Infrastructure:**
   ```bash
   # This starts PostgreSQL, Redis, Backend API, and Next.js Frontend
   docker-compose -f deploy/local/docker-compose.yml up -d
   ```

3. **Access the Application:**
   - Dashboard: http://localhost:3000
   - API Docs (Swagger): http://localhost:8000/docs

## Development Guidelines

### Backend (Python / FastAPI)
* We use **Python 3.11+**.
* All new endpoints should be fully typed with Pydantic models.
* Use `async` / `await` for all I/O bound operations (Database, Kubernetes API).
* Write tests for new analyzers using `pytest`.

### Frontend (Next.js / React)
* We use **Next.js 14 App Router** with TypeScript.
* Styling is done via **Tailwind CSS** and components from **shadcn/ui**.
* Keep components small, modular, and use React Server Components where appropriate.

## How to Contribute

### Adding a New Playbook
Playbooks are YAML files located in the `/playbooks` directory. If you have an idea for auto-remediating a common Kubernetes issue:
1. Create a new YAML file in `/playbooks`.
2. Follow the existing schema (`trigger`, `remediation` steps).
3. Open a Pull Request!

### Adding a New Analyzer
1. Create your analyzer class in `backend/app/analyzers/`.
2. Ensure it follows the interface pattern of taking `cluster_data` and returning insights.
3. Register it in the main API pipeline.

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md or `docs/` with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the reviewer to merge it for you.

## Dual License Notice

k8s-inspector operates under a dual-license model (AGPLv3 for open source, Commercial for enterprise). 
By submitting a Pull Request, you agree to our Contributor License Agreement (CLA), which allows us to distribute your contributions under both licenses while you retain copyright.

Thank you for contributing! 🚀
