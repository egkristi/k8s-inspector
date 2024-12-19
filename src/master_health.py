#!/usr/bin/env python3

"""
OpenShift Master Health Analyzer
-------------------------------
This tool performs READ-ONLY health checks on OpenShift master nodes and cluster components.
It does not make any modifications to the cluster or its configuration.
All operations are strictly observational and reporting-focused.
"""

import yaml
import os
import json
import time
from rich.console import Console
from rich.table import Table
from kubernetes import client
from kubernetes.dynamic import DynamicClient
from openshift.dynamic import DynamicClient as OpenShiftDynamicClient
import urllib3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import requests
import kubernetes

console = Console()

class MasterHealth:
    """
    OpenShift Master Health Checker
    ------------------------------
    Performs read-only health checks on OpenShift master nodes and related components.
    This checker NEVER makes any changes to the cluster - all operations are strictly
    for monitoring and reporting purposes.
    """

    def __init__(self, dyn_client, k8s_client):
        """Initialize the health checker with an OpenShift client"""
        self.dyn_client = dyn_client
        self.k8s_client = k8s_client

    def check_master_nodes(self) -> List[Dict]:
        """Check health status of master nodes"""
        try:
            # Get master nodes using OpenShift API
            nodes = self.dyn_client.resources.get(api_version='v1', kind='Node')
            master_nodes = nodes.get(
                label_selector='node-role.kubernetes.io/master'
            )
            
            results = []
            for node in master_nodes.items:
                node_status = {
                    'name': node.metadata.name,
                    'status': 'Healthy',
                    'issues': [],
                    'warnings': []
                }
                
                # Check node conditions
                for condition in node.status.conditions:
                    if condition.type == 'Ready' and condition.status != 'True':
                        node_status['status'] = 'Unhealthy'
                        node_status['issues'].append(f"Node not ready: {condition.message}")
                    elif condition.type in ['DiskPressure', 'MemoryPressure', 'PIDPressure'] and condition.status == 'True':
                        node_status['status'] = 'Warning'
                        node_status['warnings'].append(f"{condition.type}: {condition.message}")
                
                results.append(node_status)
            
            if not results:
                console.print("[yellow]Warning: No master nodes found[/yellow]")
            
            return results
        except Exception as e:
            console.print(f"[red]Error checking master nodes: {e}[/red]")
            return [{'name': 'unknown', 'status': 'Error', 'issues': [str(e)], 'warnings': []}]

    def _get_paginated_pods(self, namespace: str, label_selector: str = None) -> List:
        """Get pods with pagination"""
        try:
            pods = []
            v1 = kubernetes.client.CoreV1Api(self.k8s_client)
            
            # Get first page of pods
            pod_list = v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector,
                limit=100
            )
            
            if not pod_list:
                return []
                
            pods.extend(pod_list.items)
            
            # Continue getting pods if there are more pages
            while pod_list.metadata._continue:
                pod_list = v1.list_namespaced_pod(
                    namespace=namespace,
                    label_selector=label_selector,
                    limit=100,
                    _continue=pod_list.metadata._continue
                )
                if pod_list and pod_list.items:
                    pods.extend(pod_list.items)
                else:
                    break
            
            return pods
            
        except kubernetes.client.rest.ApiException as e:
            console.print(f"[red]Error getting pods: {e}[/red]")
            return []
        except Exception as e:
            console.print(f"[red]Unexpected error getting pods: {e}[/red]")
            return []

    def _get_paginated_response(self, api_call, *args, **kwargs):
        """Make API call with pagination to handle large responses"""
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Set a small limit and get the first page
                kwargs['limit'] = 50
                response = api_call(*args, **kwargs)
                
                # Get remaining items if there are more
                items = response.items
                while response.metadata._continue:
                    kwargs['_continue'] = response.metadata._continue
                    response = api_call(*args, **kwargs)
                    items.extend(response.items)
                
                return items
            except Exception as e:
                console.print(f"[yellow]Warning: API call failed, attempt {retry_count + 1} of {max_retries}... ({e})[/yellow]")
                retry_count += 1
                last_error = e
                
                if retry_count < max_retries:
                    time.sleep(1)  # Wait before retrying
                    continue
        
        raise Exception(f"Failed after {max_retries} attempts. Last error: {last_error}")

    def check_etcd_health(self) -> Dict:
        """Check etcd cluster health"""
        try:
            # Get etcd operator status
            operators = self.dyn_client.resources.get(
                api_version='config.openshift.io/v1',
                kind='ClusterOperator'
            )
            etcd_operator_list = operators.get(field_selector='metadata.name=etcd')
            
            if not etcd_operator_list or not hasattr(etcd_operator_list, 'items') or not etcd_operator_list.items:
                return {
                    'status': 'Error',
                    'error': 'Unable to find etcd operator'
                }
            
            etcd_operator = etcd_operator_list.items[0]
            
            # Check operator conditions
            if hasattr(etcd_operator, 'status') and hasattr(etcd_operator.status, 'conditions'):
                for condition in etcd_operator.status.conditions:
                    if condition.type == 'Degraded' and condition.status == 'True':
                        return {
                            'status': 'Unhealthy',
                            'issues': [condition.message]
                        }
                    elif condition.type == 'Available' and condition.status != 'True':
                        return {
                            'status': 'Unhealthy',
                            'issues': [f"etcd operator not available: {condition.message}"]
                        }
            
            # Get etcd pods
            etcd_pods = self._get_paginated_pods(
                namespace='openshift-etcd',
                label_selector='app=etcd'
            )
            
            if not etcd_pods:
                return {
                    'status': 'Error',
                    'error': 'No etcd pods found'
                }
            
            # Check each etcd pod's status
            unhealthy_pods = []
            for pod in etcd_pods:
                if not hasattr(pod, 'status'):
                    unhealthy_pods.append(f"{pod.metadata.name}: Unable to get pod status")
                    continue
                    
                if pod.status.phase != 'Running':
                    unhealthy_pods.append(f"{pod.metadata.name}: {pod.status.phase}")
                elif hasattr(pod.status, 'container_statuses'):
                    for container in pod.status.container_statuses:
                        if not container.ready:
                            unhealthy_pods.append(f"{pod.metadata.name}: container {container.name} not ready")
            
            if unhealthy_pods:
                return {
                    'status': 'Unhealthy',
                    'issues': unhealthy_pods
                }
            
            return {
                'status': 'Healthy',
                'message': 'All etcd pods are running and ready'
            }
            
        except Exception as e:
            console.print(f"[red]Error checking etcd health: {e}[/red]")
            return {
                'status': 'Error',
                'error': str(e)
            }

    def check_api_server_health(self) -> Dict:
        """Check API server health status"""
        try:
            pods = self.dyn_client.resources.get(api_version='v1', kind='Pod')
            api_pods = pods.get(
                namespace='openshift-kube-apiserver',
                label_selector='app=openshift-kube-apiserver'
            )
            
            api_status = {
                'healthy_servers': 0,
                'total_servers': len(api_pods.items),
                'pod_status': {}
            }
            
            for pod in api_pods.items:
                pod_status = {
                    'ready': pod.status.container_statuses[0].ready if pod.status.container_statuses else False,
                    'restarts': pod.status.container_statuses[0].restart_count if pod.status.container_statuses else 0,
                    'phase': pod.status.phase
                }
                api_status['pod_status'][pod.metadata.name] = pod_status
                if pod_status['ready']:
                    api_status['healthy_servers'] += 1
            
            # Check API endpoint health
            api_status['endpoint_healthy'] = self._check_api_endpoint()
            return api_status
            
        except Exception as e:
            console.print(f"[red]Error checking API server health: {e}[/red]")
            return {'error': str(e)}

    def _check_api_endpoint(self) -> bool:
        """Check if the API endpoint is responding"""
        try:
            response = requests.get(
                f"https://api.cluster.com:6443/healthz",
                verify=False,
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def check_critical_operators(self) -> List[Dict]:
        """Check status of critical cluster operators"""
        try:
            # Get cluster operators using OpenShift API
            operators = self.dyn_client.resources.get(
                api_version='config.openshift.io/v1',
                kind='ClusterOperator'
            )
            operator_list = operators.get()
            
            results = []
            for operator in operator_list.items:
                operator_status = {
                    'name': operator.metadata.name,
                    'status': 'Healthy',
                    'issues': []
                }
                
                # Check conditions
                if hasattr(operator.status, 'conditions'):
                    for condition in operator.status.conditions:
                        if condition.type == 'Degraded' and condition.status == 'True':
                            operator_status['status'] = 'Unhealthy'
                            operator_status['issues'].append(condition.message)
                        elif condition.type == 'Progressing' and condition.status == 'True':
                            operator_status['status'] = 'Warning'
                            operator_status['issues'].append(f"Operator is progressing: {condition.message}")
                        elif condition.type == 'Available' and condition.status != 'True':
                            operator_status['status'] = 'Unhealthy'
                            operator_status['issues'].append(f"Operator not available: {condition.message}")
                
                results.append(operator_status)
            
            return results
        except Exception as e:
            console.print(f"[red]Error checking critical operators: {e}[/red]")
            return [{'name': 'unknown', 'status': 'Error', 'issues': [str(e)]}]

    def check_control_plane_pods(self) -> List[Dict]:
        """Check status of critical control plane pods"""
        critical_namespaces = [
            'openshift-etcd',
            'openshift-apiserver',
            'openshift-kube-apiserver',
            'openshift-kube-controller-manager',
            'openshift-kube-scheduler'
        ]
        
        results = []
        try:
            # Process pods by namespace
            for namespace in critical_namespaces:
                found_control_plane_pods = False
                namespace_pods = self._get_paginated_pods(namespace=namespace)
                
                if not namespace_pods:
                    results.append({
                        'name': f'no-pods-in-{namespace}',
                        'namespace': namespace,
                        'status': 'Warning',
                        'issues': [f"No pods found in namespace {namespace}"]
                    })
                    continue
                
                for pod in namespace_pods:
                    # Skip non-control plane pods
                    if not any(component in pod.metadata.name for component in 
                             ['etcd', 'apiserver', 'controller-manager', 'scheduler']):
                        continue
                    
                    found_control_plane_pods = True
                    pod_status = {
                        'name': pod.metadata.name,
                        'namespace': namespace,
                        'status': 'Healthy',
                        'issues': []
                    }
                    
                    # Check pod phase
                    if not hasattr(pod, 'status'):
                        pod_status['status'] = 'Error'
                        pod_status['issues'].append("Unable to get pod status")
                    elif pod.status.phase != 'Running':
                        pod_status['status'] = 'Unhealthy'
                        pod_status['issues'].append(f"Pod not running: {pod.status.phase}")
                    elif hasattr(pod.status, 'container_statuses'):
                        for container in pod.status.container_statuses:
                            if not container.ready:
                                pod_status['status'] = 'Unhealthy'
                                pod_status['issues'].append(f"Container {container.name} not ready")
                    
                    results.append(pod_status)
                
                if not found_control_plane_pods:
                    results.append({
                        'name': f'no-control-plane-pods-in-{namespace}',
                        'namespace': namespace,
                        'status': 'Warning',
                        'issues': [f"No control plane pods found in namespace {namespace}"]
                    })
            
            if not results:
                return [{
                    'name': 'unknown',
                    'namespace': 'unknown',
                    'status': 'Error',
                    'issues': ["No control plane pods found in any namespace"]
                }]
                
            return results
            
        except Exception as e:
            console.print(f"[red]Error checking control plane pods: {e}[/red]")
            return [{
                'name': 'unknown',
                'namespace': 'unknown',
                'status': 'Error',
                'issues': [str(e)]
            }]

    def check_certificates(self) -> Dict:
        """Check OpenShift certificates status"""
        try:
            # Get configmap containing certificate information
            configmaps = self.dyn_client.resources.get(api_version='v1', kind='ConfigMap')
            cert_configmaps = configmaps.get(
                namespace='openshift-config-managed',
                label_selector='config.openshift.io/component=Certificates'
            )
            
            if not cert_configmaps or not hasattr(cert_configmaps, 'items'):
                return {
                    'status': 'Error',
                    'error': 'Certificate status configmap not found'
                }
            
            # Parse certificate data from all matching configmaps
            issues = []
            for cm in cert_configmaps.items:
                if hasattr(cm, 'data'):
                    for cert_name, cert_info in cm.data.items():
                        if 'expiring' in cert_info.lower() or 'expired' in cert_info.lower():
                            issues.append(f"Certificate {cert_name} is {cert_info}")
            
            if issues:
                return {
                    'status': 'Warning',
                    'issues': issues
                }
            
            return {
                'status': 'Healthy',
                'message': 'All certificates are valid'
            }
            
        except Exception as e:
            return {
                'status': 'Error',
                'error': str(e)
            }

    def generate_health_report(self, master_status, operator_status, control_plane_status, etcd_status, cert_status):
        """Generate and display a comprehensive health report"""
        console.print(f"\nOpenShift Cluster Health Report")
        console.print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Check master nodes
        table = Table(title="Master Nodes Status")
        table.add_column("Node Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Issues", style="red")
        table.add_column("Warnings", style="yellow")
        
        for node in master_status:
            table.add_row(
                node['name'],
                node['status'],
                str(node['issues'] or 'None'),
                str(node['warnings'] or 'None')
            )
        console.print(table)
        console.print("")
        
        # Check critical operators
        table = Table(title="Critical Operators Status")
        table.add_column("Operator", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Issues", style="red")
        
        for operator in operator_status:
            table.add_row(
                operator['name'],
                operator['status'],
                str(operator['issues'] or 'None')
            )
        console.print(table)
        console.print("")
        
        # Check control plane components
        table = Table(title="Control Plane Components Status")
        table.add_column("Component", style="cyan")
        table.add_column("Namespace", style="blue")
        table.add_column("Status", style="green")
        table.add_column("Issues", style="red")
        
        for component in control_plane_status:
            table.add_row(
                component['name'],
                component['namespace'],
                component['status'],
                str(component['issues'] or 'None')
            )
        console.print(table)
        console.print("")
        
        # Check etcd health
        console.print("etcd Cluster Status")
        if etcd_status['status'] == 'Healthy':
            console.print(f"[green]{etcd_status.get('message', 'Healthy')}[/green]")
        else:
            console.print(f"[red]Error: {etcd_status.get('error') or etcd_status.get('issues', ['Unknown error'])[0]}[/red]")
        console.print("")
        
        # Check certificates
        console.print("Certificate Status")
        if cert_status['status'] == 'Healthy':
            console.print(f"[green]{cert_status.get('message', 'All certificates are valid')}[/green]")
        else:
            console.print(f"[red]Error: {cert_status.get('error') or cert_status.get('issues', ['Unknown error'])[0]}[/red]")
        console.print("")

    def generate_master_health_report(self) -> None:
        """Generate a comprehensive health report for master nodes"""
        master_status = self.check_master_nodes()
        etcd_status = self.check_etcd_health()
        api_status = self.check_api_server_health()
        operator_status = self.check_critical_operators()
        control_plane_status = self.check_control_plane_pods()
        cert_status = self.check_certificates()
        
        self.generate_health_report(master_status, operator_status, control_plane_status, etcd_status, cert_status)

def main():
    try:
        # Disable SSL warnings for self-signed certificates
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Load Kubernetes config
        config.load_kube_config()
        
        # Configure to accept self-signed certificates
        configuration = client.Configuration.get_default_copy()
        configuration.verify_ssl = False
        configuration.assert_hostname = False
        
        # Create OpenShift clients
        k8s_client = client.ApiClient(configuration)
        dyn_client = OpenShiftDynamicClient(k8s_client)
        
        checker = MasterHealth(dyn_client, k8s_client)
        checker.generate_master_health_report()
    except Exception as e:
        console.print(f"[red]Error running master health checks: {e}[/red]")

if __name__ == "__main__":
    main()
