"""Pydantic schemas for Playbook YAML validation."""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
import re

class RemediationStep(BaseModel):
    """A single step in a remediation playbook."""
    step: str = Field(..., description="Name of the step")
    action: str = Field(..., description="Command or action to execute (e.g., kubectl patch...)")
    condition: Optional[str] = Field(None, alias="if", description="Optional condition for this step")

class PlaybookApproval(BaseModel):
    """Approval requirements for a playbook."""
    required: bool = Field(default=False, description="Whether manual approval is required")
    exceptions: List[str] = Field(default_factory=list, description="Namespaces or environments that bypass approval")

class PlaybookSchema(BaseModel):
    """Schema for validating Playbook YAML files."""
    name: str = Field(..., description="Unique name of the playbook")
    description: str = Field(..., description="Human-readable description")
    trigger: str = Field(..., description="Expression evaluating when to trigger (e.g. security_insight.rule == 'CIS-5.2.1')")
    remediation: List[RemediationStep] = Field(..., min_length=1, description="List of actions to perform")
    approval: Optional[PlaybookApproval] = Field(default_factory=PlaybookApproval)

    @field_validator('trigger')
    def validate_trigger_syntax(cls, v):
        # Basic check to ensure it looks like a condition
        if not re.search(r'[=<>!]+', v):
            raise ValueError("Trigger must contain a conditional operator (==, !=, >, <)")
        return v
