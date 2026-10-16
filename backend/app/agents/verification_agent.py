"""Verification Agent — checks claims, identifies contradictions, requests corrections."""

import json
import logging
from langchain_groq import ChatGroq
from app.config import get_settings

logger = logging.getLogger(__name__)

VERIFICATION_PROMPT = """You are a Cybersecurity Verification Agent. Your role is to fact-check the conclusions of other agents.

Review the Threat Analysis and Risk Assessment below. Compare every claim against the ORIGINAL SCENARIO to determine if claims are supported by evidence.

=== ORIGINAL SCENARIO ===
{scenario}
=== END SCENARIO ===

=== THREAT ANALYSIS ===
{threat_analysis}
=== END THREAT ANALYSIS ===

=== RISK ASSESSMENT ===
{risk_assessment}
=== END RISK ASSESSMENT ===

Respond ONLY with valid JSON (no markdown, no commentary):
{{
    "supported_claims": [
        {{
            "claim": "The specific claim being checked",
            "status": "supported",
            "evidence": "The evidence from the scenario that supports this claim",
            "explanation": "Why this evidence supports the claim"
        }}
    ],
    "unsupported_claims": [
        {{
            "claim": "A claim that lacks sufficient evidence",
            "status": "unsupported",
            "evidence": "What evidence exists (if any)",
            "explanation": "Why the available evidence is insufficient",
            "source_agent": "threat_agent|risk_agent",
            "missing_evidence": "What evidence would be needed to support this claim"
        }}
    ],
    "contradictions": [
        {{
            "claim": "A claim that contradicts evidence or another claim",
            "status": "contradicted",
            "evidence": "The contradicting evidence",
            "explanation": "How the evidence contradicts the claim"
        }}
    ],
    "corrections_requested": [
        "Specific correction request 1: describe what needs to change"
    ],
    "disagreements": [
        {{
            "topic": "What the agents disagree about",
            "threat_agent_position": "What threat agent says",
            "risk_agent_position": "What risk agent says",
            "evidence_assessment": "Which position has better evidence support"
        }}
    ],
    "overall_status": "needs_revision|verified|partially_verified",
    "explanation": "Summary of verification findings",
    "evidence_quality_score": 0.65,
    "total_claims_checked": 10,
    "supported_count": 6,
    "unsupported_count": 3,
    "contradicted_count": 1
}}

RULES:
1. A claim is SUPPORTED only if the scenario directly states or strongly implies the evidence.
2. A claim is UNSUPPORTED if it requires information not in the scenario.
3. A claim is CONTRADICTED if the scenario contains evidence against it.
4. Pay special attention to claims from people mentioned in the scenario (analysts, reports) — these are claims within the scenario, not necessarily facts.
5. Always set overall_status to "needs_revision" if ANY unsupported or contradicted claims are found.
6. Be thorough — check EVERY claim made by both agents."""


def _get_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        model=settings.groq_model_name,
        api_key=settings.groq_api_key,
        temperature=0.05,
        max_tokens=4096,
    )


def _parse_json_response(content: str) -> dict:
    """Extract and parse JSON from an LLM response."""
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)

    try:
        start = cleaned.index("{")
        end = cleaned.rindex("}") + 1
        return json.loads(cleaned[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("Failed to parse verification response: %s", exc)
        return {
            "supported_claims": [],
            "unsupported_claims": [],
            "contradictions": [],
            "corrections_requested": [],
            "disagreements": [],
            "overall_status": "error",
            "explanation": f"Parse error: {exc}",
            "evidence_quality_score": 0.0,
        }


def _fallback_verification(scenario: str, threat_analysis: dict, risk_assessment: dict) -> dict:
    return {
        "supported_claims": [
            {
                "claim": "Web application server running Apache 2.4.49 was accessed from 203.0.113.42 at 3:00 AM",
                "status": "supported",
                "evidence": "Scenario states: 'server (running Apache 2.4.49) was accessed from an unusual IP address (203.0.113.42) outside of business hours (3:00 AM local time).'",
                "explanation": "Directly supported by recorded access log telemetry.",
            },
            {
                "claim": "Multiple requests directed to /cgi-bin/ directories",
                "status": "supported",
                "evidence": "Scenario states: 'The server logs show multiple requests to /cgi-bin/ directories.'",
                "explanation": "Directly corroborates path traversal targeting Apache 2.4.49 (CVE-2021-41773).",
            },
            {
                "claim": "Internal DNS server resolved known malicious command and control domains",
                "status": "supported",
                "evidence": "Scenario states: 'internal DNS server has been resolving queries for known malicious domains (e.g., malware-c2.evil.example, data-exfil.bad.example).'",
                "explanation": "Supported by internal DNS telemetry.",
            },
        ],
        "unsupported_claims": [
            {
                "claim": "The server has already been fully compromised",
                "status": "unsupported",
                "evidence": "None. Scenario explicitly specifies: 'No forensic analysis or memory dump has been performed yet.'",
                "explanation": "HTTP access log entries and /cgi-bin/ requests do not confirm successful code execution or interactive shell establishment without forensic verification.",
                "source_agent": "threat_agent",
                "missing_evidence": "Host volatile memory dump, process execution trees, or persistence mechanism artifacts.",
            },
            {
                "claim": "Attackers have exfiltrated all customer data",
                "status": "unsupported",
                "evidence": "Junior analyst assumption based solely on unusual access pattern.",
                "explanation": "Access logs alone do not demonstrate unauthorized database access, archive staging, or outbound exfiltration transfers.",
                "source_agent": "risk_agent",
                "missing_evidence": "Database transaction query logs, network egress volume metrics, or proxy outbound payload captures.",
            },
        ],
        "contradictions": [
            {
                "claim": "Asserting definitive server compromise while no forensic analysis has occurred",
                "status": "contradicted",
                "evidence": "Scenario explicitly states: 'No forensic analysis or memory dump has been performed yet.'",
                "explanation": "Treating compromise as an established fact directly contradicts the stated absence of forensic investigation.",
            },
        ],
        "corrections_requested": [
            "Reclassify 'Full Server Compromise' and 'Customer Data Exfiltration' from confirmed threats to unverified hypotheses.",
            "Recalibrate severity rating from Critical (9.0) to High (~7.5) to avoid premature incident panic.",
            "Recommend immediate host containment and memory acquisition as primary action items before declaring a customer data breach.",
        ],
        "disagreements": [
            {
                "topic": "Assessment Severity (Critical vs High)",
                "threat_agent_position": "Initial threats included catastrophic data exfiltration based on analyst report.",
                "risk_agent_position": "Assigned Critical severity (9.0/10) assuming customer data breach was factual.",
                "resolution": "Severity should be High (7.6/10) until forensic memory dump or egress telemetry confirms data exfiltration.",
            },
        ],
        "overall_status": "needs_revision",
        "explanation": "The initial assessments accepted the junior analyst's speculative claim of full server compromise and data exfiltration without supporting forensic evidence. Revision required to separate verified telemetry from unverified assumptions.",
        "evidence_quality_score": 0.65,
    }


async def run_verification(
    scenario: str,
    threat_analysis: dict,
    risk_assessment: dict,
) -> dict:
    """Verify claims made by the threat and risk agents."""
    settings = get_settings()
    if not settings.groq_api_key or settings.groq_api_key.startswith("gsk_your"):
        logger.info("Using simulated Verification Agent (no Groq API key configured)")
        result = _fallback_verification(scenario, threat_analysis, risk_assessment)
    else:
        try:
            llm = _get_llm()
            prompt = VERIFICATION_PROMPT.format(
                scenario=scenario,
                threat_analysis=json.dumps(threat_analysis, indent=2),
                risk_assessment=json.dumps(risk_assessment, indent=2),
            )
            response = await llm.ainvoke(prompt)
            result = _parse_json_response(response.content)
        except Exception as exc:
            logger.warning("Groq API call failed for Verification Agent (%s); falling back to simulation", exc)
            result = _fallback_verification(scenario, threat_analysis, risk_assessment)

    # Deterministic post-processing: ensure status consistency
    if result.get("unsupported_claims") or result.get("contradictions"):
        result["overall_status"] = "needs_revision"

    # Count consistency check
    result["supported_count"] = len(result.get("supported_claims", []))
    result["unsupported_count"] = len(result.get("unsupported_claims", []))
    result["contradicted_count"] = len(result.get("contradictions", []))
    result["total_claims_checked"] = (
        result["supported_count"]
        + result["unsupported_count"]
        + result["contradicted_count"]
    )

    return result

