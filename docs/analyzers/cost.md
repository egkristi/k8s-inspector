# Cost Optimization & GreenOps

The Cost Analyzer Engine continuously evaluates cluster resources to identify waste, over-provisioning, and environmental impact.

## Features
* **GitOps Rightsizing:** Instead of just alerting on over-provisioned deployments, automatically generate Pull Requests to fix `requests` and `limits` in your Helm or YAML files.
* **GreenOps via eBPF:** Integrates with Kepler to track real power consumption (Watts) and carbon emissions (CO2) directly per pod, helping with ESG/CSRD reporting.
* **Agentic AI Cost Explainer:** Ask the system in plain English why costs spiked (e.g., "Why did AWS cost jump 30%?"), powered by an opt-in LLM.
* **Bare-Metal Pricing:** First-class support for on-premise clusters with hardware depreciation calculation and real-time electricity spot price integration.
* **Waste Detection:** Identifies orphaned PVCs and unused LoadBalancers.
