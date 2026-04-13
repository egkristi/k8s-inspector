"""Service for Agentic AI Troubleshooting (LLM Integration)."""

import logging
import httpx
import json
from typing import Dict, Any, Optional

from ..core.config import settings

logger = logging.getLogger(__name__)

class AgenticAIService:
    """Integrates with local (Ollama) or remote LLMs to explain Kubernetes failures."""
    
    def __init__(self):
        self.enabled = getattr(settings, "LLM_ENABLED", False)
        self.provider = getattr(settings, "LLM_PROVIDER", "ollama") # ollama, openai
        self.api_key = getattr(settings, "LLM_API_KEY", "")
        self.endpoint = getattr(settings, "LLM_ENDPOINT", "http://localhost:11434/api/generate")
        self.model = getattr(settings, "LLM_MODEL", "qwen2.5-coder")

    async def explain_failure(self, resource_context: Dict[str, Any], logs: str, events: list) -> Dict[str, str]:
        """
        Takes Kubernetes context and returns a plain-English explanation.
        """
        if not self.enabled:
            return {"status": "skipped", "message": "LLM Integration is disabled."}

        prompt = self._build_prompt(resource_context, logs, events)
        
        try:
            explanation = await self._call_llm(prompt)
            return {"status": "success", "explanation": explanation}
        except Exception as e:
            logger.error(f"Failed to generate LLM explanation: {e}")
            return {"status": "error", "message": str(e)}

    def _build_prompt(self, context: Dict[str, Any], logs: str, events: list) -> str:
        """Constructs a context-rich prompt for the LLM."""
        return f"""
        You are an expert Kubernetes reliability engineer. Analyze the following failure context and provide a concise, plain-English explanation of the root cause, followed by a concrete recommendation to fix it.

        Resource: {context.get('kind', 'Unknown')} {context.get('name', 'Unknown')} in namespace {context.get('namespace', 'default')}
        Status: {context.get('status', 'Unknown')}

        Recent Events:
        {json.dumps(events, indent=2)}

        Recent Logs:
        {logs[-2000:]}  # Last 2000 chars

        Format your response as:
        1. Root Cause Analysis
        2. Recommended Fix
        """

    async def _call_llm(self, prompt: str) -> str:
        """Makes the actual API call to the configured LLM provider."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            if self.provider == "ollama":
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                return response.json().get("response", "No response generated.")
            elif self.provider == "openai":
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}]
                }
                response = await client.post(self.endpoint, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")

llm_service = AgenticAIService()
