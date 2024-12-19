#!/bin/bash

# OpenShift/Kubernetes Cluster Health Check Script
# This script performs comprehensive health and performance checks on clusters

# Set color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default configuration
INTRUSIVE=false
VERBOSE=false

# Threshold configurations
THRESHOLD_POD_RESTART_COUNT=5              # Number of restarts that indicates a problem
THRESHOLD_NODE_CPU_PERCENT=80              # CPU percentage that indicates high usage
THRESHOLD_NODE_MEMORY_PERCENT=80           # Memory percentage that indicates high usage
THRESHOLD_PV_USAGE_PERCENT=85              # Storage usage percentage that indicates high usage
THRESHOLD_EVENTS_WINDOW_MINUTES=60         # Time window for relevant events in minutes
THRESHOLD_PENDING_POD_COUNT=5              # Number of pending pods that indicates a problem
THRESHOLD_FAILED_POD_COUNT=3               # Number of failed pods that indicates a problem
THRESHOLD_CERTIFICATE_EXPIRY_DAYS=30       # Days before certificate expiry to warn
THRESHOLD_CONTAINER_MEMORY_PERCENT=90      # Container memory usage percentage that indicates high usage
THRESHOLD_CONTAINER_CPU_PERCENT=90         # Container CPU usage percentage that indicates high usage

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --intrusive)
            INTRUSIVE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [--intrusive] [--verbose]"
            exit 1
            ;;
    esac
done

# Function to print section headers
print_section() {
    local title="$1"
    local width=80
    local padding=$(( (width - ${#title} - 2) / 2 ))
    local line=$(printf '%*s' "$width" | tr ' ' '=')
    
    echo -e "\n${CYAN}${line}${NC}"
    printf "${CYAN}%*s${BOLD} %s ${NC}${CYAN}%*s${NC}\n" $padding '' "$title" $padding ''
    echo -e "${CYAN}${line}${NC}\n"
}

# Function for verbose logging
log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[VERBOSE] $1${NC}"
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    if ! command -v oc &> /dev/null && ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: Neither 'oc' nor 'kubectl' command found. Please install the appropriate CLI.${NC}"
        exit 1
    fi

    # Determine if we're on OpenShift or plain Kubernetes
    if command -v oc &> /dev/null && oc status &> /dev/null; then
        export CLUSTER_TYPE="OpenShift"
        export CLI_TOOL="oc"
    else
        export CLUSTER_TYPE="Kubernetes"
        export CLI_TOOL="kubectl"
    fi

    if ! $CLI_TOOL auth can-i get nodes &> /dev/null; then
        echo -e "${RED}Error: Insufficient permissions. Please ensure you have cluster-admin privileges.${NC}"
        exit 1
    fi

    echo -e "${GREEN}Prerequisites check passed${NC}"
    echo "Cluster Type: $CLUSTER_TYPE"
    echo "CLI Tool: $CLI_TOOL"
}

# Function to check control plane health
check_control_plane() {
    print_section "Checking Control Plane Health"
    
    # Check API Server
    echo "Checking API Server status..."
    $CLI_TOOL get --raw /healthz &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ API Server is healthy${NC}"
    else
        echo -e "${RED}✗ API Server health check failed${NC}"
    fi

    # Check Controller Manager
    echo "Checking Controller Manager..."
    if [ "$CLUSTER_TYPE" = "OpenShift" ]; then
        CONTROLLER_NS="openshift-kube-controller-manager"
    else
        CONTROLLER_NS="kube-system"
    fi
    $CLI_TOOL get pods -n $CONTROLLER_NS | grep -i "controller-manager" | grep -v "Running" && \
        echo -e "${RED}✗ Controller Manager issues detected${NC}" || \
        echo -e "${GREEN}✓ Controller Manager is healthy${NC}"

    # Check Scheduler
    echo "Checking Scheduler..."
    if [ "$CLUSTER_TYPE" = "OpenShift" ]; then
        SCHEDULER_NS="openshift-kube-scheduler"
    else
        SCHEDULER_NS="kube-system"
    fi
    $CLI_TOOL get pods -n $SCHEDULER_NS | grep -i "scheduler" | grep -v "Running" && \
        echo -e "${RED}✗ Scheduler issues detected${NC}" || \
        echo -e "${GREEN}✓ Scheduler is healthy${NC}"
}

# Function to check cluster operators (OpenShift specific)
check_cluster_operators() {
    if [ "$CLUSTER_TYPE" = "OpenShift" ]; then
        print_section "Checking Cluster Operators"
        
        DEGRADED_OPERATORS=$($CLI_TOOL get clusteroperators -o json | jq -r '.items[] | select(.status.conditions[] | select(.type=="Degraded" and .status=="True")) | .metadata.name')
        if [ -n "$DEGRADED_OPERATORS" ]; then
            echo -e "${RED}The following operators are degraded:${NC}"
            echo "$DEGRADED_OPERATORS"
        else
            echo -e "${GREEN}✓ All cluster operators are healthy${NC}"
        fi
    fi
}

# Function to check node health
check_nodes() {
    print_section "Checking Node Health"
    
    # Check node status
    echo "Node Status:"
    $CLI_TOOL get nodes -o wide
    
    # Check for NotReady nodes
    NOT_READY=$($CLI_TOOL get nodes | grep -i "NotReady" | wc -l)
    if [ $NOT_READY -gt 0 ]; then
        echo -e "${RED}Warning: $NOT_READY node(s) are NotReady${NC}"
    fi
    
    # Check node resource usage
    echo -e "\nNode Resource Usage:"
    $CLI_TOOL adm top nodes
    
    # Check for pressure conditions
    echo -e "\nChecking for node pressure conditions..."
    $CLI_TOOL get nodes -o json | jq -r '
        .items[] | select(.status.conditions != null) | 
        .metadata.name as $name |
        .status.conditions[] |
        select(.type | endswith("Pressure")) |
        select(.status == "True") |
        "\($name): \(.type)"
    ' | while read line; do
        if [ ! -z "$line" ]; then
            echo -e "${RED}Node pressure detected: $line${NC}"
        fi
    done
}

# Function to check pod health
check_pods() {
    print_section "Checking Pod Health"
    
    # Check for pods not in Running/Completed state
    echo "Pods not in Running/Completed state:"
    PENDING_PODS=$($CLI_TOOL get pods --all-namespaces -o wide | grep -c "Pending")
    FAILED_PODS=$($CLI_TOOL get pods --all-namespaces -o wide | grep -c "Failed")
    
    if [ $PENDING_PODS -gt $THRESHOLD_PENDING_POD_COUNT ]; then
        echo -e "${RED}Warning: $PENDING_PODS pods in Pending state (threshold: $THRESHOLD_PENDING_POD_COUNT)${NC}"
    fi
    if [ $FAILED_PODS -gt $THRESHOLD_FAILED_POD_COUNT ]; then
        echo -e "${RED}Warning: $FAILED_PODS pods in Failed state (threshold: $THRESHOLD_FAILED_POD_COUNT)${NC}"
    fi
    
    $CLI_TOOL get pods --all-namespaces -o wide | grep -v "Running\|Completed" || echo -e "${GREEN}✓ All pods are running or completed${NC}"
    
    # Check for pods with high restart counts
    HIGH_RESTARTS=$($CLI_TOOL get pods --all-namespaces -o json | jq -r --arg threshold "$THRESHOLD_POD_RESTART_COUNT" '
        .items[] | 
        select(.status.containerStatuses != null) | 
        .metadata.namespace as $ns |
        .metadata.name as $name |
        .status.containerStatuses[] |
        select(.restartCount > ($threshold|tonumber)) |
        "\($ns)/\($name): \(.restartCount) restarts"
    ')
    if [ ! -z "$HIGH_RESTARTS" ]; then
        echo -e "\nPods with high restart counts (>$THRESHOLD_POD_RESTART_COUNT):"
        echo "$HIGH_RESTARTS"
    fi
    
    # Check for pods with image pull issues
    echo -e "\nPods with image pull issues:"
    $CLI_TOOL get pods --all-namespaces -o json | jq -r '.items[] | select(.status.containerStatuses != null) | select(.status.containerStatuses[].state.waiting.reason == "ImagePullBackOff" or .status.containerStatuses[].state.waiting.reason == "ErrImagePull") | "\(.metadata.namespace)/\(.metadata.name)"' || echo -e "${GREEN}✓ No image pull issues detected${NC}"
}

# Function to check persistent volumes
check_storage() {
    print_section "Checking Storage Status"
    
    # Check PV status
    echo "PersistentVolume Status:"
    $CLI_TOOL get pv
    
    # Check for failed PVCs
    echo -e "\nPersistentVolumeClaims with issues:"
    $CLI_TOOL get pvc --all-namespaces | grep -v "Bound" || echo -e "${GREEN}✓ All PVCs are bound${NC}"
    
    # Check storage classes
    echo -e "\nStorage Classes:"
    $CLI_TOOL get sc
}

# Function to check networking
check_networking() {
    print_section "Checking Network Status"
    
    # Check network policies
    if [ "$VERBOSE" = true ]; then
        echo "Network Policies:"
        $CLI_TOOL get networkpolicies --all-namespaces || echo "No network policies found"
    else
        echo "Namespaces missing Network Policies:"
        # Get all namespaces except system ones
        NAMESPACES=$($CLI_TOOL get namespaces -o json | jq -r '
            .items[] | 
            select(.metadata.name | 
                test("^(kube-|openshift-|default|kubernetes-dashboard)") | not
            ) | 
            .metadata.name
        ')
        
        # Check each namespace for network policies
        for ns in $NAMESPACES; do
            NETPOL_COUNT=$($CLI_TOOL get networkpolicies -n $ns -o json | jq '.items | length')
            if [ "$NETPOL_COUNT" -eq 0 ]; then
                echo -e "${YELLOW}$ns${NC}"
            fi
        done
    fi
    
    # Check services
    echo -e "\nServices without endpoints:"
    SERVICES_WITHOUT_ENDPOINTS=()
    while read -r svc; do
        if [ ! -z "$svc" ]; then
            NS=$(echo $svc | cut -d' ' -f1)
            NAME=$(echo $svc | cut -d' ' -f2)
            ENDPOINTS=$($CLI_TOOL get endpoints $NAME -n $NS -o json | jq '.subsets[]?.addresses[]?.ip' 2>/dev/null)
            if [ -z "$ENDPOINTS" ]; then
                SERVICES_WITHOUT_ENDPOINTS+=("$NS/$NAME")
            fi
        fi
    done < <($CLI_TOOL get services --all-namespaces -o json | jq -r '.items[] | select(.spec.type!="ExternalName") | "\(.metadata.namespace) \(.metadata.name)"')

    COUNT=${#SERVICES_WITHOUT_ENDPOINTS[@]}
    if [ $COUNT -gt 0 ]; then
        echo -e "${YELLOW}Found $COUNT service(s) without endpoints${NC}"
        if [ "$VERBOSE" = true ]; then
            echo "Detailed list:"
            printf '%s\n' "${SERVICES_WITHOUT_ENDPOINTS[@]}"
        fi
    else
        echo -e "${GREEN}✓ All services have endpoints${NC}"
    fi
    
    if [ "$CLUSTER_TYPE" = "OpenShift" ]; then
        # Check routes
        echo -e "\nRoute Status:"
        $CLI_TOOL get routes --all-namespaces
    else
        # Check ingresses
        echo -e "\nIngress Status:"
        $CLI_TOOL get ingress --all-namespaces
    fi
}

# Function to check security
check_security() {
    print_section "Checking Security Status"
    
    # Check certificate expiration
    if [ "$CLUSTER_TYPE" = "OpenShift" ]; then
        echo "Checking certificate expiration..."
        $CLI_TOOL get apiserver -o jsonpath='{.items[*].status.conditions[?(@.type=="Encrypted")].status}'
    fi
    
    # Check pod security policies/security context constraints
    if [ "$CLUSTER_TYPE" = "OpenShift" ]; then
        echo -e "\nSecurity Context Constraints:"
        $CLI_TOOL get scc
    else
        echo -e "\nPod Security Policies:"
        $CLI_TOOL get psp 2>/dev/null || echo "No Pod Security Policies found"
    fi
    
    # Check service accounts
    echo -e "\nService Accounts with elevated permissions:"
    $CLI_TOOL get clusterrolebindings -o json | jq -r '.items[] | select(.subjects[]?.kind == "ServiceAccount") | "\(.metadata.name): \(.subjects[]?.namespace)/\(.subjects[]?.name)"'
}

# Function to check resource usage
check_resource_usage() {
    print_section "Checking Resource Usage"
    
    # Check namespace resource quotas
    echo "Resource Quotas:"
    $CLI_TOOL get resourcequotas --all-namespaces
    
    # Check limit ranges
    echo -e "\nLimit Ranges:"
    $CLI_TOOL get limitranges --all-namespaces
    
    # Show top resource-consuming pods
    echo -e "\nPods with high CPU usage (>$THRESHOLD_CONTAINER_CPU_PERCENT%):"
    $CLI_TOOL adm top pods --all-namespaces | awk -v threshold=$THRESHOLD_CONTAINER_CPU_PERCENT 'NR>1 && $4>threshold{print}' | sort -k4 -rn | head -10
    
    echo -e "\nPods with high memory usage (>$THRESHOLD_CONTAINER_MEMORY_PERCENT%):"
    $CLI_TOOL adm top pods --all-namespaces | awk -v threshold=$THRESHOLD_CONTAINER_MEMORY_PERCENT 'NR>1 && $6>threshold{print}' | sort -k6 -rn | head -10
}

# Function to perform intrusive diagnostics
perform_intrusive_checks() {
    print_section "Performing Intrusive Diagnostics"
    echo -e "${RED}Warning: Running intrusive checks that may impact cluster performance${NC}"
    
    # Test API server responsiveness under load
    echo "Testing API server responsiveness..."
    for i in {1..50}; do
        $CLI_TOOL get nodes >/dev/null 2>&1 &
    done
    wait
    
    # Test pod scheduling
    echo "Testing pod scheduling..."
    $CLI_TOOL create deployment test-scheduling --image=nginx --replicas=1
    sleep 5
    $CLI_TOOL delete deployment test-scheduling
    
    # Check node draining capability
    echo "Testing node drain capability (dry-run)..."
    RANDOM_NODE=$($CLI_TOOL get nodes -o name | shuf -n 1)
    $CLI_TOOL drain $RANDOM_NODE --dry-run=true --delete-emptydir-data --ignore-daemonsets
    
    # Test cluster autoscaling (if enabled)
    echo "Testing cluster autoscaling responsiveness..."
    $CLI_TOOL get clusterautoscaler >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        $CLI_TOOL create deployment autoscale-test --image=nginx --replicas=10
        sleep 10
        $CLI_TOOL delete deployment autoscale-test
    fi
}

# Function to check DNS
check_dns() {
    print_section "Checking DNS Status"
    
    # Check CoreDNS/KubeDNS pods
    if [ "$CLUSTER_TYPE" = "OpenShift" ]; then
        DNS_NAMESPACE="openshift-dns"
    else
        DNS_NAMESPACE="kube-system"
    fi
    
    echo "DNS Pods Status:"
    $CLI_TOOL get pods -n $DNS_NAMESPACE | grep -E "coredns|kubedns"
    
    # Test DNS resolution if intrusive checks are enabled
    if [ "$INTRUSIVE" = true ]; then
        echo -e "\nTesting DNS resolution..."
        $CLI_TOOL run dns-test --image=busybox --rm -it --restart=Never -- nslookup kubernetes.default.svc.cluster.local
    fi
}

# Main execution
main() {
    echo -e "${YELLOW}Starting Comprehensive Cluster Health Check${NC}"
    echo "Timestamp: $(date)"
    
    check_prerequisites
    check_control_plane
    check_cluster_operators
    check_nodes
    check_pods
    check_storage
    check_networking
    check_security
    check_resource_usage
    check_dns
    
    if [ "$INTRUSIVE" = true ]; then
        echo -e "\n${RED}Running intrusive checks - this may impact cluster performance${NC}"
        perform_intrusive_checks
    fi
    
    echo -e "\n${GREEN}Health check completed${NC}"
    
    # Summary of findings
    print_section "Summary"
    echo "Cluster Type: $CLUSTER_TYPE"
    echo "Total Nodes: $($CLI_TOOL get nodes --no-headers | wc -l)"
    echo "NotReady Nodes: $($CLI_TOOL get nodes --no-headers | grep -i "NotReady" | wc -l)"
    echo "Total Namespaces: $($CLI_TOOL get namespaces --no-headers | wc -l)"
    echo "Total Pods: $($CLI_TOOL get pods --all-namespaces --no-headers | wc -l)"
    echo "Pods Not Running: $($CLI_TOOL get pods --all-namespaces --no-headers | grep -v "Running\|Completed" | wc -l)"
}

# Run main function
main
