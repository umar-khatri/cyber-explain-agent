"""Assessment API routes — submit scenarios and retrieve results."""

import logging
from fastapi import APIRouter, HTTPException
from app.models import ScenarioRequest, AssessmentResponse
from app.agents.graph import run_assessment_pipeline
from app.database import store_assessment, get_assessment, get_all_assessments

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["assessment"])

# ── Sample scenario ─────────────────────────────────────────────────

SAMPLE_SCENARIO = """Our company's web application server (running Apache 2.4.49) was accessed from an \
unusual IP address (203.0.113.42) outside of business hours (3:00 AM local time). \
The server logs show multiple requests to /cgi-bin/ directories. \
Additionally, our internal DNS server has been resolving queries for known malicious domains \
(e.g., malware-c2.evil.example, data-exfil.bad.example). \
A junior analyst reviewed the logs and claims that the server has already been fully compromised \
and that attackers have exfiltrated all customer data, based solely on the unusual access pattern. \
No forensic analysis or memory dump has been performed yet."""


@router.get("/sample-scenario")
async def get_sample_scenario():
    """Return the built-in sample scenario."""
    return {"scenario": SAMPLE_SCENARIO}


@router.post("/assess", response_model=AssessmentResponse)
async def run_assessment(request: ScenarioRequest):
    """Submit a cybersecurity scenario for multi-agent assessment.

    This triggers the full pipeline:
    1. Threat Agent → identifies threats
    2. Risk Agent → assesses severity
    3. Verification Agent → checks claims
    4. (Conditional) Revision → corrects unsupported claims
    5. Final Assessment → combined result
    """
    logger.info("Starting assessment for scenario (%d chars)", len(request.scenario))
    try:
        result = await run_assessment_pipeline(request.scenario)

        # Persist to Supabase
        try:
            await store_assessment(result)
            logger.info("Assessment %s stored in Supabase", result["id"])
        except Exception as db_err:
            # Don't fail the request if DB write fails
            logger.warning("Failed to store in Supabase (assessment still returned): %s", db_err)

        return AssessmentResponse(**result)

    except Exception as exc:
        logger.exception("Assessment pipeline failed")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(exc)}")


@router.get("/assessments")
async def list_assessments():
    """List all previous assessments."""
    try:
        data = await get_all_assessments()
        items = []
        for row in data:
            fa = row.get("final_assessment") or {}
            items.append({
                "id": row["id"],
                "scenario": row["scenario"][:150] + "..." if len(row.get("scenario", "")) > 150 else row.get("scenario", ""),
                "severity": fa.get("severity", "Unknown"),
                "created_at": row.get("created_at", ""),
            })
        return {"assessments": items}
    except Exception as exc:
        logger.warning("Failed to list assessments: %s", exc)
        return {"assessments": []}


@router.get("/assessments/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment_detail(assessment_id: str):
    """Retrieve a single assessment with full trace."""
    try:
        data = await get_assessment(assessment_id)
        if not data:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return AssessmentResponse(**data)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to retrieve assessment")
        raise HTTPException(status_code=500, detail=str(exc))
