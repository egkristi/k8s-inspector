"""Service for GitOps Auto-PRs (Automated Rightsizing and Remediation)."""

import logging
import httpx
import base64
from typing import Dict, Any, Optional

from ..core.config import settings

logger = logging.getLogger(__name__)

class GitOpsService:
    """Creates Pull Requests in GitHub/GitLab to automatically fix issues in code."""
    
    def __init__(self):
        self.enabled = getattr(settings, "GITOPS_ENABLED", False)
        self.provider = getattr(settings, "GITOPS_PROVIDER", "github") # github, gitlab
        self.token = getattr(settings, "GITOPS_TOKEN", "")
        
    async def create_remediation_pr(self, repo: str, filepath: str, insight: Dict[str, Any], proposed_change: str) -> Dict[str, str]:
        """
        Creates a Pull Request in the target repository to apply a remediation.
        """
        if not self.enabled or not self.token:
            logger.warning("GitOps is disabled or missing token.")
            return {"status": "skipped", "message": "GitOps integration is disabled."}

        logger.info(f"Creating GitOps PR for {repo} -> {filepath}")
        
        try:
            if self.provider == "github":
                return await self._create_github_pr(repo, filepath, insight, proposed_change)
            else:
                return {"status": "error", "message": f"Unsupported GitOps provider: {self.provider}"}
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return {"status": "error", "message": str(e)}

    async def _create_github_pr(self, repo: str, filepath: str, insight: Dict[str, Any], proposed_change: str) -> Dict[str, str]:
        """GitHub specific PR creation logic."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        async with httpx.AsyncClient(base_url="https://api.github.com") as client:
            # 1. Get default branch & latest commit SHA
            repo_res = await client.get(f"/repos/{repo}", headers=headers)
            repo_res.raise_for_status()
            default_branch = repo_res.json()["default_branch"]
            
            ref_res = await client.get(f"/repos/{repo}/git/ref/heads/{default_branch}", headers=headers)
            ref_res.raise_for_status()
            base_sha = ref_res.json()["object"]["sha"]

            # 2. Create a new branch
            new_branch = f"k8s-inspector-fix-{insight.get('id', 'unknown')}"
            await client.post(
                f"/repos/{repo}/git/refs",
                headers=headers,
                json={"ref": f"refs/heads/{new_branch}", "sha": base_sha}
            )

            # 3. Get existing file content
            file_res = await client.get(f"/repos/{repo}/contents/{filepath}?ref={new_branch}", headers=headers)
            file_res.raise_for_status()
            file_data = file_res.json()
            file_sha = file_data["sha"]
            
            # (In a real scenario, we would parse the YAML, apply `proposed_change`, and serialize back)
            # For MVP architecture, we assume proposed_change is the full new file content
            content_b64 = base64.b64encode(proposed_change.encode("utf-8")).decode("utf-8")

            # 4. Commit the change
            commit_message = f"chore(k8s-inspector): Auto-remediation for {insight.get('title', 'issue')}"
            await client.put(
                f"/repos/{repo}/contents/{filepath}",
                headers=headers,
                json={
                    "message": commit_message,
                    "content": content_b64,
                    "sha": file_sha,
                    "branch": new_branch
                }
            )

            # 5. Create the PR
            pr_res = await client.post(
                f"/repos/{repo}/pulls",
                headers=headers,
                json={
                    "title": f"k8s-inspector 🐦‍⬛: {insight.get('title', 'Auto-Remediation')}",
                    "body": f"### Automated Kubernetes Remediation\n\n**Reason:** {insight.get('description')}\n**Recommendation:** {insight.get('recommendation')}\n\n*Created by k8s-inspector 2.0*",
                    "head": new_branch,
                    "base": default_branch
                }
            )
            pr_res.raise_for_status()
            pr_url = pr_res.json()["html_url"]

            return {"status": "success", "pr_url": pr_url}

gitops_service = GitOpsService()
