"""Insights API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db

router = APIRouter()


@router.get("")
async def list_insights(
    cluster_id: Optional[int] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List AI-generated insights, optionally filtered."""
    # TODO: Query insights table
    return []


@router.get("/{insight_id}")
async def get_insight(insight_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific insight with full details."""
    return {"id": insight_id, "status": "not_found"}


@router.patch("/{insight_id}/acknowledge")
async def acknowledge_insight(insight_id: int, db: AsyncSession = Depends(get_db)):
    """Mark an insight as acknowledged."""
    return {"id": insight_id, "status": "acknowledged"}


@router.patch("/{insight_id}/dismiss")
async def dismiss_insight(insight_id: int, db: AsyncSession = Depends(get_db)):
    """Dismiss an insight."""
    return {"id": insight_id, "status": "dismissed"}
