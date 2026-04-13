"""Playbook execution engine for automated remediation."""

import logging
import yaml
import os
from typing import Dict, Any, List
from kubernetes import client

from ..services.cluster_service import cluster_service

logger = logging.getLogger(__name__)

class PlaybookService:
    """Loads and executes auto-remediation playbooks against clusters."""
    
    def __init__(self):
        self.playbooks_dir = os.path.join(os.path.dirname(__file__), "../../../playbooks")
        self.playbooks = {}
        self._load_playbooks()
        
    def _load_playbooks(self):
        """Load and validate all YAML playbooks from the playbooks directory."""
        from ..models.playbook import PlaybookSchema
        from pydantic import ValidationError
        
        if not os.path.exists(self.playbooks_dir):
            logger.warning(f"Playbooks directory not found: {self.playbooks_dir}")
            return
            
        for filename in os.listdir(self.playbooks_dir):
            if filename.endswith(('.yaml', '.yml')):
                filepath = os.path.join(self.playbooks_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        raw_playbook = yaml.safe_load(f)
                        
                        # Validate against Pydantic schema
                        try:
                            playbook = PlaybookSchema(**raw_playbook)
                            self.playbooks[playbook.name] = playbook.model_dump()
                            logger.info(f"Loaded and validated playbook: {playbook.name}")
                        except ValidationError as ve:
                            logger.error(f"Validation error in playbook {filename}:\n{ve}")
                            
                except Exception as e:
                    logger.error(f"Failed to load playbook {filename}: {e}")

    def get_available_playbooks(self) -> List[Dict[str, str]]:
        """Return list of available playbooks."""
        return [
            {"id": k, "description": v.get("description", "No description")}
            for k, v in self.playbooks.items()
        ]

    async def execute_playbook(self, playbook_name: str, cluster_id: int, target_resource: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute a playbook against a specific cluster and resource.
        
        Args:
            playbook_name: Name of the playbook to run
            cluster_id: Target cluster ID
            target_resource: Dict with kind, name, namespace
            
        Returns:
            Dict with execution results
        """
        if playbook_name not in self.playbooks:
            return {"status": "error", "message": f"Playbook '{playbook_name}' not found."}
            
        playbook = self.playbooks[playbook_name]
        logger.info(f"Executing playbook {playbook_name} on cluster {cluster_id}")
        
        results = {
            "playbook": playbook_name,
            "target": target_resource,
            "status": "success",
            "steps_executed": [],
            "logs": []
        }
        
        try:
            # Note: In MVP, we just mock the execution steps based on the playbook definition.
            # Real implementation would parse the 'action' field and make respective k8s API calls.
            
            remediation_steps = playbook.get("remediation", [])
            for step in remediation_steps:
                action = step.get("action", "")
                
                if action.startswith("patch deployment"):
                    # Mocking the K8s API call
                    results["steps_executed"].append(step.get("step"))
                    results["logs"].append(f"Successfully patched {target_resource.get('kind')} {target_resource.get('name')}")
                    
                elif action.startswith("kubectl apply"):
                    results["steps_executed"].append(step.get("step"))
                    results["logs"].append(f"Applied manifest for {step.get('step')}")
                    
        except Exception as e:
            logger.error(f"Playbook execution failed: {e}")
            results["status"] = "failed"
            results["message"] = str(e)
            
        return results

# Singleton
playbook_service = PlaybookService()
