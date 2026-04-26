"""Service for Kubernetes cluster operations."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging

try:
    from openshift.dynamic import DynamicClient
    HAS_OPENSHIFT = True
except ImportError:
    HAS_OPENSHIFT = False

from ..core.config import settings

logger = logging.getLogger(__name__)


class ClusterService:
    """Service for interacting with Kubernetes clusters."""
    
    def __init__(self):
        self.clients: Dict[int, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def get_cluster_client(self, cluster_id: int, kubeconfig_path: str) -> Dict[str, Any]:
        """Get or create Kubernetes client for a cluster."""
        async with self._lock:
            if cluster_id not in self.clients:
                try:
                    # Load kubeconfig (sync call, run in thread)
                    if kubeconfig_path:
                        await asyncio.to_thread(config.load_kube_config, config_file=kubeconfig_path)
                    else:
                        await asyncio.to_thread(config.load_kube_config)
                    
                    # Create clients
                    api_client = client.ApiClient()
                    v1 = client.CoreV1Api(api_client)
                    apps_v1 = client.AppsV1Api(api_client)
                    
                    # Try OpenShift dynamic client
                    dynamic_client = None
                    cluster_type = "kubernetes"
                    if HAS_OPENSHIFT:
                        try:
                            dynamic_client = DynamicClient(api_client)
                            # Test OpenShift-specific API
                            await asyncio.to_thread(
                                dynamic_client.resources.get,
                                api_version='config.openshift.io/v1',
                                kind='ClusterOperator',
                            )
                            cluster_type = "openshift"
                        except Exception:
                            cluster_type = "kubernetes"
                    
                    self.clients[cluster_id] = {
                        "v1": v1,
                        "apps_v1": apps_v1,
                        "dynamic": dynamic_client,
                        "cluster_type": cluster_type,
                        "created_at": datetime.now(),
                    }
                    
                    logger.info(f"Created client for cluster {cluster_id} (type: {cluster_type})")
                    
                except Exception as e:
                    logger.error(f"Failed to create client for cluster {cluster_id}: {e}")
                    raise
            
            # Update last seen
            self.clients[cluster_id]["last_seen"] = datetime.now()
            return self.clients[cluster_id]
    
    async def get_cluster_version(self, cluster_client: Dict[str, Any]) -> str:
        """Get Kubernetes version."""
        try:
            v1 = cluster_client["v1"]
            version_info = await asyncio.to_thread(v1.get_api_versions)
            return version_info.git_version
        except Exception as e:
            logger.error(f"Failed to get cluster version: {e}")
            return "unknown"
    
    async def get_nodes(self, cluster_client: Dict[str, Any]) -> List[Dict]:
        """Get all nodes in cluster."""
        try:
            v1 = cluster_client["v1"]
            nodes = await asyncio.to_thread(v1.list_node)
            
            return [
                {
                    "name": node.metadata.name,
                    "status": self._get_node_status(node),
                    "roles": self._get_node_roles(node),
                    "version": node.status.node_info.kubelet_version,
                    "cpu_capacity": self._parse_resource(node.status.capacity.get("cpu", "0")),
                    "memory_capacity": self._parse_resource(node.status.capacity.get("memory", "0")),
                    "conditions": [
                        {
                            "type": c.type,
                            "status": c.status,
                            "message": c.message if c.message else None,
                        }
                        for c in node.status.conditions
                    ],
                }
                for node in nodes.items
            ]
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            return []
    
    def _get_node_status(self, node) -> str:
        """Determine node status from conditions."""
        for condition in node.status.conditions:
            if condition.type == "Ready":
                return "Ready" if condition.status == "True" else "NotReady"
        return "Unknown"
    
    def _get_node_roles(self, node) -> List[str]:
        """Get node roles from labels."""
        roles = []
        labels = node.metadata.labels or {}
        
        if "node-role.kubernetes.io/master" in labels:
            roles.append("master")
        elif "node-role.kubernetes.io/control-plane" in labels:
            roles.append("control-plane")
        
        if "node-role.kubernetes.io/worker" in labels:
            roles.append("worker")
        
        if not roles:
            roles.append("worker")  # Default
        
        return roles
    
    def _parse_resource(self, value: str) -> float:
        """Parse Kubernetes resource value to numeric."""
        if not value:
            return 0.0
        
        value = str(value)
        multipliers = {
            'm': 0.001,  # milli
            'K': 1000,
            'M': 1000000,
            'G': 1000000000,
            'T': 1000000000000,
            'Ki': 1024,
            'Mi': 1024 ** 2,
            'Gi': 1024 ** 3,
            'Ti': 1024 ** 4,
        }
        
        for suffix, mult in multipliers.items():
            if value.endswith(suffix):
                return float(value[:-len(suffix)]) * mult
        
        return float(value)
    
    async def get_pods_by_namespace(self, cluster_client: Dict[str, Any], namespace: str = None) -> List[Dict]:
        """Get pods, optionally filtered by namespace."""
        try:
            v1 = cluster_client["v1"]
            
            if namespace:
                pods = await asyncio.to_thread(v1.list_namespaced_pod, namespace=namespace)
            else:
                pods = await asyncio.to_thread(v1.list_pod_for_all_namespaces)
            
            return [
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "restart_count": sum(
                        cs.restart_count for cs in (pod.status.container_statuses or [])
                    ),
                    "ready": self._is_pod_ready(pod),
                    "age": self._calculate_age(pod.metadata.creation_timestamp),
                }
                for pod in pods.items
            ]
        except Exception as e:
            logger.error(f"Failed to get pods: {e}")
            return []
    
    def _is_pod_ready(self, pod) -> bool:
        """Check if pod is ready."""
        if not pod.status.container_statuses:
            return False
        return all(cs.ready for cs in pod.status.container_statuses)
    
    def _calculate_age(self, creation_timestamp) -> str:
        """Calculate pod age."""
        if not creation_timestamp:
            return "unknown"
        
        now = datetime.now(creation_timestamp.tzinfo)
        delta = now - creation_timestamp
        
        if delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600}h"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60}m"
        else:
            return f"{delta.seconds}s"
    
    async def get_namespaces(self, cluster_client: Dict[str, Any]) -> List[Dict]:
        """Get all namespaces."""
        try:
            v1 = cluster_client["v1"]
            namespaces = await asyncio.to_thread(v1.list_namespace)
            
            return [
                {
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                    "created": ns.metadata.creation_timestamp.isoformat() if ns.metadata.creation_timestamp else None,
                }
                for ns in namespaces.items
            ]
        except Exception as e:
            logger.error(f"Failed to get namespaces: {e}")
            return []
    
    async def get_cluster_operators(self, cluster_client: Dict[str, Any]) -> List[Dict]:
        """Get OpenShift cluster operators."""
        if cluster_client.get("cluster_type") != "openshift" or not cluster_client.get("dynamic"):
            return []
        
        try:
            dynamic = cluster_client["dynamic"]
            operators = await asyncio.to_thread(
                dynamic.resources.get,
                api_version='config.openshift.io/v1',
                kind='ClusterOperator',
            )
            operator_list = await asyncio.to_thread(operators.get)
            
            return [
                {
                    "name": op.metadata.name,
                    "available": self._check_operator_condition(op, "Available"),
                    "progressing": self._check_operator_condition(op, "Progressing"),
                    "degraded": self._check_operator_condition(op, "Degraded"),
                }
                for op in operator_list.items
            ]
        except Exception as e:
            logger.error(f"Failed to get cluster operators: {e}")
            return []
    
    def _check_operator_condition(self, operator, condition_type: str) -> bool:
        """Check if operator has a specific condition."""
        if not hasattr(operator, 'status') or not hasattr(operator.status, 'conditions'):
            return False
        
        for condition in operator.status.conditions:
            if condition.type == condition_type:
                return condition.status == "True"
        
        return False


# Singleton instance
cluster_service = ClusterService()
