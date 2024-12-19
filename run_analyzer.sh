#!/bin/bash

# Exit on any error
set -e

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create virtual environment if it doesn't exist
[ ! -d "venv" ] && python3 -m venv venv > /dev/null 2>&1

# Activate virtual environment and install dependencies silently
source venv/bin/activate
python -m pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

# Check for kubeconfig
if [ -z "${KUBECONFIG}" ]; then
    if [ -f ~/.kube/config ]; then
        export KUBECONFIG=~/.kube/config
    else
        echo -e "${RED}Error: No kubeconfig found. Please set KUBECONFIG environment variable or place your kubeconfig at ~/.kube/config${NC}"
        exit 1
    fi
fi

# Run the analyzer
echo -e "${GREEN}Running OpenShift Health Analysis...${NC}\n"
python src/main.py

# Deactivate virtual environment
deactivate > /dev/null 2>&1
