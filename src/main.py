#!/usr/bin/env python3

import os
import sys
import urllib3
from openshift.dynamic import DynamicClient
from kubernetes import client, config
from rich.console import Console
from datetime import datetime
from master_health import MasterHealth

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()

def setup_client():
    """Initialize OpenShift client"""
    try:
        # Load OpenShift configuration from default location
        kubeconfig = os.getenv('KUBECONFIG', os.path.expanduser('~/.kube/config'))
        
        # Configure client to accept self-signed certificates
        configuration = client.Configuration()
        config.load_kube_config(kubeconfig, client_configuration=configuration)
        configuration.verify_ssl = False
        configuration.assert_hostname = False
        
        k8s_client = client.ApiClient(configuration)
        dyn_client = DynamicClient(k8s_client)
        
        # Test connectivity
        version = dyn_client.resources.get(api_version='v1', kind='ClusterVersion')
        if not version:
            raise Exception("Failed to connect to OpenShift cluster")
        
        console.print("[green]Successfully connected to OpenShift cluster[/green]")
        return dyn_client, k8s_client
        
    except Exception as e:
        console.print(f"[red]Error connecting to OpenShift cluster: {e}[/red]")
        console.print("[yellow]Please ensure you have a valid kubeconfig file and are logged into your cluster[/yellow]")
        sys.exit(1)

def main():
    """Main function"""
    try:
        # Setup OpenShift client
        dyn_client, k8s_client = setup_client()
        
        # Initialize health checker
        health_checker = MasterHealth(dyn_client, k8s_client)
        
        # Generate health report
        health_checker.generate_master_health_report()
        
    except Exception as e:
        console.print(f"[red]Error running health checks: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
