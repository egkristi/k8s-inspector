"""Cost analysis engine for Kubernetes clusters."""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CostAnalyzer:
    """Analyze Kubernetes cluster costs and identify optimization opportunities."""
    
    def __init__(self):
        # Cloud provider pricing (simplified - would use APIs in production)
        self.pricing = {
            "cpu_per_hour": 0.035,  # $ per vCPU per hour
            "memory_gb_per_hour": 0.005,  # $ per GB RAM per hour
            "storage_gb_per_month": 0.10,  # $ per GB SSD per month
            "load_balancer_per_month": 25.0,  # $ per LB per month
            "nat_gateway_per_hour": 0.045,  # $ per NAT gateway per hour
        }
    
    async def analyze_cluster(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze cluster costs and generate optimization recommendations.
        
        Args:
            cluster_data: Dict with nodes, pods, pvcs, services, etc.
        
        Returns:
            Dict with cost breakdown, waste detection, and recommendations
        """
        result = {
            "cluster_id": cluster_data.get("id"),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "currency": "USD",
            "current_monthly_cost": 0.0,
            "optimized_monthly_cost": 0.0,
            "potential_savings": 0.0,
            "savings_percentage": 0.0,
            "breakdown": {},
            "waste_detection": [],
            "recommendations": [],
        }
        
        # Calculate compute costs
        compute_cost = self._calculate_compute_cost(cluster_data.get("nodes", []))
        result["breakdown"]["compute"] = compute_cost
        
        # Calculate storage costs
        storage_cost = self._calculate_storage_cost(cluster_data.get("pvcs", []))
        result["breakdown"]["storage"] = storage_cost
        
        # Calculate network costs
        network_cost = self._calculate_network_cost(cluster_data.get("services", []))
        result["breakdown"]["network"] = network_cost
        
        # Total current cost
        result["current_monthly_cost"] = (
            compute_cost["monthly"] + storage_cost["monthly"] + network_cost["monthly"]
        )
        
        # Detect waste
        waste = self._detect_waste(cluster_data)
        result["waste_detection"] = waste
        
        # Calculate optimized cost
        total_waste = sum(item.get("monthly_waste", 0) for item in waste)
        result["optimized_monthly_cost"] = result["current_monthly_cost"] - total_waste
        result["potential_savings"] = total_waste
        
        if result["current_monthly_cost"] > 0:
            result["savings_percentage"] = (
                total_waste / result["current_monthly_cost"] * 100
            )
        
        # Generate recommendations
        result["recommendations"] = self._generate_recommendations(waste, cluster_data)
        
        return result
    
    def _calculate_compute_cost(self, nodes: List[Dict]) -> Dict[str, float]:
        """Calculate compute costs from nodes."""
        total_cpu = 0.0
        total_memory_gb = 0.0
        
        for node in nodes:
            cpu = node.get("cpu_capacity", 0)
            memory = node.get("memory_capacity", 0)
            
            # Convert to standard units if needed
            if cpu > 100:  # Likely in millicores
                cpu = cpu / 1000
            if memory > 1000000000:  # Likely in bytes
                memory = memory / (1024 ** 3)  # Convert to GB
            
            total_cpu += cpu
            total_memory_gb += memory
        
        hourly_cost = (
            total_cpu * self.pricing["cpu_per_hour"] +
            total_memory_gb * self.pricing["memory_gb_per_hour"]
        )
        
        return {
            "hourly": hourly_cost,
            "daily": hourly_cost * 24,
            "monthly": hourly_cost * 24 * 30,
            "total_cpu": total_cpu,
            "total_memory_gb": total_memory_gb,
        }
    
    def _calculate_storage_cost(self, pvcs: List[Dict]) -> Dict[str, float]:
        """Calculate storage costs from PVCs."""
        total_storage_gb = 0.0
        
        for pvc in pvcs:
            storage = pvc.get("capacity_gb", 0)
            total_storage_gb += storage
        
        monthly_cost = total_storage_gb * self.pricing["storage_gb_per_month"]
        
        return {
            "monthly": monthly_cost,
            "total_storage_gb": total_storage_gb,
        }
    
    def _calculate_network_cost(self, services: List[Dict]) -> Dict[str, float]:
        """Calculate network costs from services."""
        load_balancers = sum(
            1 for svc in services if svc.get("type") == "LoadBalancer"
        )
        
        monthly_cost = load_balancers * self.pricing["load_balancer_per_month"]
        
        return {
            "monthly": monthly_cost,
            "load_balancer_count": load_balancers,
        }
    
    def _detect_waste(self, cluster_data: Dict[str, Any]) -> List[Dict]:
        """Detect wasted resources."""
        waste_items = []
        
        # Check for orphaned PVCs
        pvcs = cluster_data.get("pvcs", [])
        pods = cluster_data.get("pods", [])
        mounted_pvcs = set()
        
        for pod in pods:
            for volume in pod.get("volumes", []):
                if volume.get("persistentVolumeClaim"):
                    mounted_pvcs.add(volume["persistentVolumeClaim"]["claimName"])
        
        for pvc in pvcs:
            if pvc["name"] not in mounted_pvcs:
                waste_items.append({
                    "type": "orphaned_pvc",
                    "resource": f"PVC/{pvc['name']}",
                    "namespace": pvc.get("namespace", "default"),
                    "monthly_waste": pvc.get("capacity_gb", 0) * self.pricing["storage_gb_per_month"],
                    "description": f"PVC '{pvc['name']}' is not mounted by any pod",
                    "recommendation": f"Delete PVC {pvc['name']} or attach it to a pod",
                })
        
        # Check for unused load balancers
        services = cluster_data.get("services", [])
        for svc in services:
            if svc.get("type") == "LoadBalancer":
                # Check if service has endpoints
                if svc.get("endpoint_count", 0) == 0:
                    waste_items.append({
                        "type": "unused_load_balancer",
                        "resource": f"Service/{svc['name']}",
                        "namespace": svc.get("namespace", "default"),
                        "monthly_waste": self.pricing["load_balancer_per_month"],
                        "description": f"LoadBalancer '{svc['name']}' has no backend endpoints",
                        "recommendation": f"Delete LoadBalancer service {svc['name']} or add backend pods",
                    })
        
        # Check for over-provisioned deployments
        deployments = cluster_data.get("deployments", [])
        for deploy in deployments:
            requested_cpu = deploy.get("requested_cpu", 0)
            actual_cpu = deploy.get("actual_cpu", 0)
            
            if requested_cpu > 0 and actual_cpu > 0:
                utilization = actual_cpu / requested_cpu
                if utilization < 0.3:  # Less than 30% utilization
                    waste_cpu = (requested_cpu - actual_cpu) * self.pricing["cpu_per_hour"] * 24 * 30
                    waste_items.append({
                        "type": "over_provisioned_cpu",
                        "resource": f"Deployment/{deploy['name']}",
                        "namespace": deploy.get("namespace", "default"),
                        "monthly_waste": waste_cpu,
                        "description": f"CPU utilization only {utilization*100:.1f}% (requested: {requested_cpu}, actual: {actual_cpu})",
                        "recommendation": f"Reduce CPU request from {requested_cpu} to {actual_cpu * 1.3:.2f} (30% headroom)",
                    })
        
        return waste_items
    
    def _generate_recommendations(
        self,
        waste: List[Dict],
        cluster_data: Dict[str, Any],
    ) -> List[Dict]:
        """Generate actionable recommendations from waste detection."""
        recommendations = []
        
        # Group by type
        by_type = {}
        for item in waste:
            item_type = item["type"]
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)
        
        # Generate summary recommendations
        if "orphaned_pvc" in by_type:
            total_waste = sum(item["monthly_waste"] for item in by_type["orphaned_pvc"])
            recommendations.append({
                "category": "storage_optimization",
                "title": f"Delete {len(by_type['orphaned_pvc'])} orphaned PVCs",
                "description": f"These PVCs are not mounted by any pod and are wasting ${total_waste:.2f}/month",
                "estimated_savings": total_waste,
                "effort": "low",
                "risk": "low",
                "affected_resources": [item["resource"] for item in by_type["orphaned_pvc"]],
            })
        
        if "unused_load_balancer" in by_type:
            total_waste = sum(item["monthly_waste"] for item in by_type["unused_load_balancer"])
            recommendations.append({
                "category": "network_optimization",
                "title": f"Remove {len(by_type['unused_load_balancer'])} unused LoadBalancers",
                "description": f"These LoadBalancers have no backend endpoints, wasting ${total_waste:.2f}/month",
                "estimated_savings": total_waste,
                "effort": "low",
                "risk": "medium",
                "affected_resources": [item["resource"] for item in by_type["unused_load_balancer"]],
            })
        
        if "over_provisioned_cpu" in by_type:
            total_waste = sum(item["monthly_waste"] for item in by_type["over_provisioned_cpu"])
            recommendations.append({
                "category": "compute_optimization",
                "title": f"Rightsize {len(by_type['over_provisioned_cpu'])} over-provisioned deployments",
                "description": f"These deployments use less than 30% of requested CPU, wasting ${total_waste:.2f}/month",
                "estimated_savings": total_waste,
                "effort": "medium",
                "risk": "low",
                "affected_resources": [item["resource"] for item in by_type["over_provisioned_cpu"]],
            })
        
        # Sort by savings
        recommendations.sort(key=lambda x: x["estimated_savings"], reverse=True)
        
        return recommendations


# Singleton instance
cost_analyzer = CostAnalyzer()
