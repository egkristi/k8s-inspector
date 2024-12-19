# Kubernetes Cluster Health Inspector (k8s-inspector)

A comprehensive health check tool for Kubernetes clusters that performs various diagnostic checks, provides interactive troubleshooting, and generates detailed reports.

## Features

- 🔍 Comprehensive cluster health checks
- 📊 Real-time progress tracking
- 🛠 Interactive troubleshooting mode
- 📝 HTML/PDF report generation
- 📈 Monitoring system integration
- 🔄 Historical comparison
- 🚀 Automatic remediation suggestions

## Prerequisites

- Kubernetes CLI (`kubectl`)
- `jq` for JSON processing
- `yq` for YAML processing
- `wkhtmltopdf` (optional, for PDF report generation)
- Cluster admin privileges (some checks can run in unprivileged mode)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/k8s-inspector.git
cd k8s-inspector
```

2. Make the script executable:
```bash
chmod +x k8s-inspector.sh
```

## Quick Start

Run a basic health check:
```bash
./k8s-inspector.sh
```

Run with all features enabled:
```bash
./k8s-inspector.sh --all --interactive --report=html
```

## Usage

### Basic Commands

```bash
# Run essential checks only
./k8s-inspector.sh

# Run all available checks
./k8s-inspector.sh --all

# Generate HTML report
./k8s-inspector.sh --report=html
```

### Command Line Options

- `--all`: Run all available checks
- `--report=<format>`: Generate report (all/html/pdf/json/yaml/none)
- `--intrusive`: Run in intrusive mode, potentially making changes to cluster
- `--unprivileged`: Run in unprivileged mode
- `--timeout=<seconds>`: Set operation timeout
- `-h, --help`: Display help message

## Output Formats

The tool supports multiple output formats:

- Text (default): Human-readable output
- JSON: Structured output for programmatic processing
- YAML: Structured output in YAML format
- HTML/PDF: Detailed reports with styling and formatting

## Report Generation

Reports include:
- Cluster metadata
- Check results and findings
- Remediation suggestions
- Historical comparisons
- Visual indicators for issues

## Monitoring Integration

Supports integration with:
- Prometheus
- Pushgateway
- Extensible for other monitoring systems

## Historical Analysis

- Stores check results for trend analysis
- Compares current and previous results
- Identifies new and resolved issues
- Maintains 30-day history

## Security

- Supports unprivileged mode for non-admin users
- Skips privileged checks when running without admin rights
- Safe command execution with proper error handling

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation in `docs/`
2. Open an issue in the repository
3. Contact the maintainers

## Authors

Maintained by the Kubernetes Health Check Tool team.

## Acknowledgments

Thanks to all contributors and the Kubernetes community for their valuable input and support.

## Kubernetes Documentation References

For more information about the components and concepts checked by this tool, refer to the official Kubernetes documentation:

### Architecture and Administration
- [Cluster Architecture](https://kubernetes.io/docs/concepts/architecture/)
- [Cluster Administration](https://kubernetes.io/docs/concepts/cluster-administration/)
- [Backup and Restore](https://kubernetes.io/docs/tasks/administer-cluster/backup-etcd/)
- [Cluster Monitoring](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)
- [Cluster Logging](https://kubernetes.io/docs/concepts/cluster-administration/logging/)

### Security
- [Authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/)
- [Certificate Management](https://kubernetes.io/docs/tasks/tls/managing-tls-in-a-cluster/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Security Best Practices](https://kubernetes.io/docs/concepts/security/security-best-practices/)

### Core Components
- [etcd Operations](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
- [Node Management](https://kubernetes.io/docs/concepts/architecture/nodes/)
- [Pod Operations](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Network Concepts](https://kubernetes.io/docs/concepts/services-networking/)

### Storage
- [Storage Overview](https://kubernetes.io/docs/concepts/storage/volumes/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)

### Troubleshooting
- [Troubleshooting Clusters](https://kubernetes.io/docs/tasks/debug/debug-cluster/)
- [Debugging Pods](https://kubernetes.io/docs/tasks/debug/debug-application/)
- [Network Troubleshooting](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

# OpenShift Health Check Tool - Feature Documentation

## Table of Contents

1. [Health Checks](#health-checks)
2. [Progress Tracking](#progress-tracking)
3. [Interactive Mode](#interactive-mode)
4. [Report Generation](#report-generation)
5. [Monitoring Integration](#monitoring-integration)
6. [Historical Analysis](#historical-analysis)
7. [Remediation](#remediation)
8. [Output Formats](#output-formats)

## Health Checks

### Core Components
- **ETCD Health**
  - Member status
  - Performance metrics
  - Backup status
  - Disk usage
  - [ETCD Overview](https://docs.openshift.com/container-platform/latest/scalability_and_performance/recommended-host-practices.html#recommended-etcd-practices_recommended-host-practices)
  - [Backing up etcd](https://docs.openshift.com/container-platform/latest/backup_and_restore/control_plane_backup_and_restore/backing-up-etcd.html)
  - [Troubleshooting etcd](https://docs.openshift.com/container-platform/latest/support/troubleshooting/troubleshooting-etcd-issues.html)

- **Master Nodes**
  - API server health
  - Controller manager status
  - Scheduler status
  - Node conditions
  - [Understanding Operators](https://docs.openshift.com/container-platform/latest/operators/understanding/olm-what-operators-are.html)
  - [Operator Installation](https://docs.openshift.com/container-platform/latest/operators/admin/olm-adding-operators-to-cluster.html)
  - [Operator Status](https://docs.openshift.com/container-platform/latest/operators/understanding/olm-status.html)

- **Networking**
  - SDN health
  - DNS functionality
  - Load balancer status
  - Network policies
  - [Network Policy](https://docs.openshift.com/container-platform/latest/networking/network_policy/about-network-policy.html)
  - [DNS Operator](https://docs.openshift.com/container-platform/latest/networking/dns-operator.html)
  - [Ingress Operator](https://docs.openshift.com/container-platform/latest/networking/ingress-operator.html)

- **Security**
  - Certificate expiration
  - Authentication config
  - Authorization policies
  - Security context constraints
  - [Managing Certificates](https://docs.openshift.com/container-platform/latest/security/certificates/replacing-default-ingress-certificate.html)
  - [Authentication](https://docs.openshift.com/container-platform/latest/authentication/understanding-authentication.html)
  - [Authorization](https://docs.openshift.com/container-platform/latest/authentication/using-rbac.html)

### Additional Checks
- **Storage**
  - PV/PVC status
  - Storage class health
  - Volume snapshots
  - [Storage Overview](https://docs.openshift.com/container-platform/latest/storage/understanding-persistent-storage.html)
  - [Storage Classes](https://docs.openshift.com/container-platform/latest/storage/dynamic-provisioning.html)
  - [CSI Drivers](https://docs.openshift.com/container-platform/latest/storage/container_storage_interface/persistent-storage-csi.html)

- **Workload Health**
  - Pod status
  - Deployment health
  - StatefulSet status
  - DaemonSet health
  - [Resource Quotas](https://docs.openshift.com/container-platform/latest/applications/quotas/quotas-setting-per-project.html)
  - [Limit Ranges](https://docs.openshift.com/container-platform/latest/nodes/clusters/nodes-cluster-limit-ranges.html)
  - [Resource Management](https://docs.openshift.com/container-platform/latest/nodes/clusters/nodes-cluster-resource-manage.html)

- **Resource Usage**
  - CPU utilization
  - Memory consumption
  - Storage usage
  - Network throughput
  - [Monitoring Overview](https://docs.openshift.com/container-platform/latest/monitoring/monitoring-overview.html)
  - [Managing Metrics](https://docs.openshift.com/container-platform/latest/monitoring/managing-metrics.html)
  - [Prometheus Alerting](https://docs.openshift.com/container-platform/latest/monitoring/managing-alerts.html)

## Progress Tracking

### Visual Progress Bar
```
Progress [===================>---------------] 45%
```

Features:
- Real-time progress updates
- Percentage completion
- Visual bar representation
- Check count tracking

## Interactive Mode

### Activation
```bash
./openshift_check09.sh --interactive
```

### Features
- Context-aware troubleshooting
- Guided issue resolution
- Command suggestions
- Interactive prompts

### Available Actions
1. **ETCD Issues**
   - Member list inspection
   - Log analysis
   - Backup management
   - Performance tuning

2. **Network Issues**
   - Pod connectivity tests
   - DNS verification
   - Route validation
   - Policy checking

3. **Security Issues**
   - Certificate management
   - Authentication debugging
   - Authorization verification
   - SCC validation

## Report Generation

### HTML Reports
```bash
./openshift_check09.sh --report=html
```

Features:
- Styled layout
- Interactive elements
- Issue categorization
- Remediation sections

### PDF Reports
```bash
./openshift_check09.sh --report=pdf
```

Requirements:
- wkhtmltopdf installation
- Proper permissions
- Sufficient disk space

### Report Sections
1. **Executive Summary**
   - Overall health status
   - Critical issues
   - Recent changes

2. **Detailed Findings**
   - Component status
   - Error messages
   - Warning indicators
   - Success metrics

3. **Remediation Steps**
   - Action items
   - Command references
   - Best practices
   - Documentation links

## Monitoring Integration

### Prometheus Integration
```bash
./openshift_check09.sh --monitoring-url=http://prometheus:9091
```

### Metrics
- Health check status
- Issue counts
- Check duration
- Resource metrics

### Integration Options
1. **Prometheus Pushgateway**
   - Metric pushing
   - Label management
   - Time series data

2. **Custom Monitoring**
   - Extensible framework
   - Custom metric support
   - Alert integration

## Historical Analysis

### Storage
- Location: `~/.openshift_health_history`
- Retention: 30 days
- Format: Log files

### Comparison Features
- Issue tracking
- Trend analysis
- Change detection
- Progress monitoring

### Analysis Types
1. **Issue Comparison**
   - New issues
   - Resolved issues
   - Recurring problems

2. **Trend Analysis**
   - Health patterns
   - Resource usage
   - Performance metrics

## Remediation

### Automatic Suggestions
- Context-aware solutions
- Step-by-step guides
- Command examples
- Best practices

### Categories
1. **ETCD Issues**
   ```bash
   # Check member health
   oc get etcd -o=jsonpath='{range .items[0].status.conditions[?(@.type=="EtcdMembersAvailable")]}{.message}{"\n"}{end}'
   ```

2. **Node Issues**
   ```bash
   # Check resource usage
   oc adm top nodes
   ```

3. **Certificate Issues**
   ```bash
   # Check certificate status
   oc get csr
   ```

## Output Formats

### Text Format (Default)
```bash
./openshift_check09.sh --format=text
```
- Human-readable
- Color-coded
- Structured output
- Progress indicators

### JSON Format
```bash
./openshift_check09.sh --format=json
```
- Machine-readable
- Structured data
- Parsing-friendly
- Integration-ready

### YAML Format
```bash
./openshift_check09.sh --format=yaml
```
- Human-friendly
- Structured data
- Configuration-compatible
- Documentation-friendly

## Advanced Usage

### Parallel Processing
```bash
./openshift_check09.sh --parallel --max-jobs=5
```
- Faster execution
- Resource management
- Job control
- Progress tracking

### Unprivileged Mode
```bash
./openshift_check09.sh --unprivileged
```
- Limited checks
- Safe operations
- Permission awareness
- Clear limitations

### Custom Timeouts
```bash
./openshift_check09.sh --timeout=60
```
- Operation limits
- Error handling
- Safe termination
- Resource cleanup
