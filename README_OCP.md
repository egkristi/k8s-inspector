# OpenShift Health Analyzer

A comprehensive tool for analyzing OpenShift cluster performance and health metrics. This tool operates in **READ-ONLY** mode and never makes any modifications to your cluster.

## Safety Features

- **Read-Only Operations**: All checks are strictly observational and will never modify your cluster
- **Permission Verification**: The tool verifies it has read-only access at startup
- **Safe Execution**: No write operations are performed, making it safe to run in production environments

## Features

- Cluster resource utilization monitoring
- Node health analysis
- Pod performance metrics
- Alert monitoring and analysis
- Performance trend visualization
- Resource optimization recommendations

## Prerequisites

- Python 3.8+
- OpenShift CLI (oc)
- Access to an OpenShift cluster (read-only access is sufficient)
- Prometheus metrics enabled on the cluster

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your OpenShift credentials in `config.yaml`
   - Note: The tool only requires read permissions
   - If credentials have write permissions, the tool will still operate in read-only mode

## Usage

```bash
python src/main.py
```

## Configuration

Edit `config.yaml` to customize:
- Cluster connection details
- Monitoring parameters
- Alert thresholds
- Reporting preferences

## Security Notes

1. This tool is designed to be safe to run in production environments
2. No cluster modifications are ever made
3. All operations are read-only queries
4. The tool will warn if it detects it has more permissions than needed
