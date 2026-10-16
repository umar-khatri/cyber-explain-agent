"""Supabase database client and helper functions."""

import json
from typing import Optional
from supabase import create_client, Client
from app.config import get_settings


# Local in-memory fallback cache for when Supabase is not configured
_MEMORY_STORE: dict[str, dict] = {}


def get_supabase_client() -> Optional[Client]:
    """Create and return a Supabase client if configured."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_key or "your-project" in settings.supabase_url:
        return None
    try:
        return create_client(settings.supabase_url, settings.supabase_key)
    except Exception:
        return None


async def store_assessment(assessment: dict) -> dict:
    """Store a completed assessment in Supabase or memory."""
    # Always keep in local memory store as cache
    _MEMORY_STORE[assessment["id"]] = assessment

    client = get_supabase_client()
    if client:
        result = client.table("assessments").insert(assessment).execute()
        return result.data[0] if result.data else assessment
    return assessment


async def get_assessment(assessment_id: str) -> Optional[dict]:
    """Retrieve a single assessment by ID."""
    if assessment_id in _MEMORY_STORE:
        return _MEMORY_STORE[assessment_id]

    client = get_supabase_client()
    if client:
        result = (
            client.table("assessments")
            .select("*")
            .eq("id", assessment_id)
            .execute()
        )
        return result.data[0] if result.data else None
    return None


async def get_all_assessments() -> list[dict]:
    """List all assessments ordered by creation time."""
    client = get_supabase_client()
    if client:
        result = (
            client.table("assessments")
            .select("id, scenario, final_assessment, created_at")
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        if result.data:
            return result.data

    # Fallback to local memory cache
    return [
        {
            "id": v["id"],
            "scenario": v.get("scenario", ""),
            "final_assessment": v.get("final_assessment", {}),
            "created_at": v.get("created_at", ""),
        }
        for v in reversed(list(_MEMORY_STORE.values()))
    ]

