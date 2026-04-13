# Auto-Remediation Playbooks

Playbooks are YAML definitions that tell k8s-inspector how to automatically fix issues it discovers.

## Example Playbook

```yaml
name: enforce-pss-baseline
description: Applies Pod Security Standard 'baseline' to a namespace
trigger: security_insight.rule == 'CIS-5.2.1'

remediation:
  - step: apply_pss_label
    action: kubectl label namespace {{ target.namespace }} pod-security.kubernetes.io/enforce=baseline --overwrite
  
approval:
  required: true
  exceptions: [dev, staging]
```

When an insight triggers a playbook, the system will either automatically execute the remediation steps (if `approval: required: false`) or prompt an administrator in the Next.js Dashboard to approve the action.
