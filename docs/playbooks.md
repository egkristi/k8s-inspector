# Auto-Remediation Playbooks

One of the most powerful features of **k8s-inspector** is its ability to not just alert on issues, but fix them automatically. This is achieved through **Playbooks**.

Playbooks are declarative YAML files that map specific insights/alerts to a set of remediation actions.

## Playbook Structure

Every playbook must contain three main sections: `trigger`, `remediation`, and `approval`.

```yaml
name: enforce-pss-baseline
description: Applies Pod Security Standard 'baseline' to a namespace
trigger: security_insight.rule == 'CIS-5.2.1'

remediation:
  - step: apply_pss_label
    action: kubectl label namespace {{ target.namespace }} pod-security.kubernetes.io/enforce=baseline --overwrite
  
  - step: audit_pss
    action: kubectl label namespace {{ target.namespace }} pod-security.kubernetes.io/audit=restricted --overwrite

approval:
  required: true
  exceptions: [dev, staging]
```

### 1. Triggers
The `trigger` field defines the condition that causes the playbook to run. It uses a simple expression language.
* `security_insight.rule == 'CIS-5.2.1'` (Runs when a specific CIS rule is violated)
* `cost_insight.type == 'orphaned_pvc'` (Runs when an unused volume is found)
* `anomaly.type == 'memory_leak'` (Runs when the ML engine detects a memory leak)

### 2. Remediation Steps
This is an array of actions to perform. They execute sequentially. If one fails, the playbook execution stops.
Available actions include:
* `kubectl patch ...`
* `kubectl delete ...`
* `kubectl label ...`
* `slack_notify ...`

We use **Jinja2** templating (`{{ target.namespace }}`) to inject context from the insight directly into the command.

### 3. Approval Workflow
Not all actions should happen automatically in production. 
* `required: true`: The remediation will wait in a "Pending" state in the Next.js Dashboard until a human clicks "Approve".
* `exceptions: [dev, staging]`: You can configure environments where approval is *not* required, allowing full automation in lower environments.

## Creating Custom Playbooks

You can easily add your own playbooks by dropping a `.yaml` file into the `/playbooks` directory of the application. The Playbook Engine automatically scans this folder on startup and registers new workflows.
