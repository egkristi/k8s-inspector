"""Security analysis engine for Kubernetes clusters."""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SecurityAnalyzer:
    """Analyze Kubernetes cluster security posture against CIS benchmarks and best practices."""
    
    async def analyze_cluster(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze cluster security and generate compliance insights.
        
        Args:
            cluster_data: Dict with pods, nodes, roles, network_policies, etc.
            
        Returns:
            Dict with security score, compliance status, and remediation recommendations
        """
        result = {
            "cluster_id": cluster_data.get("id"),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "security_score": 100.0,
            "issues_found": 0,
            "critical_issues": 0,
            "checks": [],
            "recommendations": []
        }
        
        issues = []
        
        # 1. Check Pod Security (Privileged, Root)
        pod_issues = self._check_pod_security(cluster_data.get("pods", []))
        issues.extend(pod_issues)
        
        # 2. Check Network Policies
        network_issues = self._check_network_policies(
            cluster_data.get("namespaces", []),
            cluster_data.get("network_policies", [])
        )
        issues.extend(network_issues)
        
        # 3. Check RBAC (Over-permissive roles)
        rbac_issues = self._check_rbac(
            cluster_data.get("roles", []),
            cluster_data.get("cluster_roles", [])
        )
        issues.extend(rbac_issues)
        
        # Process results
        result["checks"] = issues
        result["issues_found"] = len(issues)
        
        critical_count = sum(1 for i in issues if i["severity"] == "critical")
        high_count = sum(1 for i in issues if i["severity"] == "high")
        medium_count = sum(1 for i in issues if i["severity"] == "medium")
        
        result["critical_issues"] = critical_count
        
        # Calculate score (100 - (critical*10) - (high*5) - (medium*2) - (low*1))
        deductions = (critical_count * 10) + (high_count * 5) + (medium_count * 2) + (len(issues) - critical_count - high_count - medium_count)
        result["security_score"] = max(0.0, 100.0 - deductions)
        
        # Generate actionable recommendations
        result["recommendations"] = self._generate_recommendations(issues)
        
        return result

    def _check_pod_security(self, pods: List[Dict]) -> List[Dict]:
        """Check pods for security misconfigurations."""
        issues = []
        
        for pod in pods:
            namespace = pod.get("namespace", "default")
            name = pod.get("name", "unknown")
            resource_ref = f"Pod/{namespace}/{name}"
            
            # Skip kube-system for basic checks
            if namespace == "kube-system":
                continue
                
            containers = pod.get("containers", [])
            for container in containers:
                sec_ctx = container.get("securityContext", {})
                
                # Check for privileged containers
                if sec_ctx.get("privileged", False):
                    issues.append({
                        "category": "pod_security",
                        "severity": "critical",
                        "rule": "CIS-5.2.1",
                        "resource": resource_ref,
                        "description": f"Container '{container.get('name')}' is running as privileged",
                        "remediation": "Remove 'privileged: true' from securityContext"
                    })
                
                # Check for root user
                if not sec_ctx.get("runAsNonRoot", False):
                    issues.append({
                        "category": "pod_security",
                        "severity": "high",
                        "rule": "CIS-5.2.6",
                        "resource": resource_ref,
                        "description": f"Container '{container.get('name')}' may run as root",
                        "remediation": "Set 'runAsNonRoot: true' in securityContext"
                    })
                    
        return issues

    def _check_network_policies(self, namespaces: List[Dict], policies: List[Dict]) -> List[Dict]:
        """Check if namespaces have default deny network policies."""
        issues = []
        namespaces_with_policies = set()
        
        for policy in policies:
            namespaces_with_policies.add(policy.get("namespace"))
            
        for ns in namespaces:
            ns_name = ns.get("name")
            if ns_name not in namespaces_with_policies and ns_name not in ["kube-system", "kube-public", "k8s-inspector"]:
                issues.append({
                    "category": "network",
                    "severity": "high",
                    "rule": "NSA-1.3",
                    "resource": f"Namespace/{ns_name}",
                    "description": f"Namespace '{ns_name}' has no NetworkPolicies defined",
                    "remediation": "Create a default deny-all NetworkPolicy for the namespace"
                })
                
        return issues

    def _check_rbac(self, roles: List[Dict], cluster_roles: List[Dict]) -> List[Dict]:
        """Check for overly permissive RBAC roles."""
        issues = []
        
        # Check ClusterRoles for wildcard permissions
        for crole in cluster_roles:
            name = crole.get("name")
            if name.startswith("system:"):  # Skip built-in
                continue
                
            for rule in crole.get("rules", []):
                verbs = rule.get("verbs", [])
                resources = rule.get("resources", [])
                
                if "*" in verbs and "*" in resources:
                    issues.append({
                        "category": "rbac",
                        "severity": "critical",
                        "rule": "CIS-5.1.1",
                        "resource": f"ClusterRole/{name}",
                        "description": "ClusterRole grants wildcard access to all resources",
                        "remediation": "Apply least privilege principle by specifying exact verbs and resources"
                    })
                    
        return issues

    def _generate_recommendations(self, issues: List[Dict]) -> List[Dict]:
        """Group issues into actionable recommendations."""
        recommendations = []
        
        # Group by category
        by_category = {}
        for issue in issues:
            cat = issue["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(issue)
            
        if "pod_security" in by_category:
            recommendations.append({
                "title": "Enforce Pod Security Standards",
                "description": f"Found {len(by_category['pod_security'])} pod security violations (root execution, privileged containers).",
                "category": "security",
                "risk_level": "high",
                "auto_fix_available": True,
                "auto_fix_playbook": "enforce-pss-baseline",
                "affected_resources": [i["resource"] for i in by_category["pod_security"]]
            })
            
        if "network" in by_category:
            recommendations.append({
                "title": "Apply Default Deny Network Policies",
                "description": f"Found {len(by_category['network'])} namespaces without network isolation.",
                "category": "security",
                "risk_level": "medium",
                "auto_fix_available": True,
                "auto_fix_playbook": "apply-default-deny-netpol",
                "affected_resources": [i["resource"] for i in by_category["network"]]
            })

        return recommendations


# Singleton instance
security_analyzer = SecurityAnalyzer()
