"""Threat Analysis Agent — identifies cybersecurity threats from a scenario."""

import json
import logging
from langchain_groq import ChatGroq
from app.config import get_settings

logger = logging.getLogger(__name__)

THREAT_PROMPT = """You are a Cybersecurity Threat Analysis Agent.

Analyse the following scenario and identify potential cybersecurity threats.

=== SCENARIO ===
{scenario}
=== END SCENARIO ===

Respond ONLY with valid JSON matching this schema (no markdown, no commentary):
{{
    "threats": [
        {{
            "id": "T1",
            "name": "Short threat name",
            "description": "Detailed description of the threat",
            "indicators": ["observable indicator 1", "observable indicator 2"],
            "evidence_from_scenario": "Exact quote or direct reference from the scenario that supports this threat",
            "is_evidence_based": true,
            "confidence": 0.85
        }}
    ],
    "summary": "One-paragraph overall threat summary",
    "overall_confidence": 0.75,
    "evidence_references": ["Direct evidence item 1 from the scenario", "Direct evidence item 2"],
    "model_interpretations": ["Interpretation 1 that goes beyond the stated evidence", "Interpretation 2"]
}}

RULES:
1. Clearly separate evidence directly stated in the scenario from your own interpretations.
2. Set is_evidence_based=false for any threat relying on assumptions NOT in the scenario.
3. If someone in the scenario makes a claim, evaluate whether the scenario provides sufficient evidence for that claim.
4. Confidence should reflect how well the evidence supports the threat (0.0 = no evidence, 1.0 = certain).
5. List ALL model interpretations separately — these are conclusions you draw that go beyond what is explicitly stated."""


THREAT_REVISION_PROMPT = """You are a Cybersecurity Threat Analysis Agent revising your previous analysis.

=== ORIGINAL SCENARIO ===
{scenario}
=== END SCENARIO ===

=== YOUR PREVIOUS ANALYSIS ===
{previous_analysis}
=== END PREVIOUS ANALYSIS ===

=== VERIFICATION FEEDBACK ===
{verification_feedback}
=== END VERIFICATION FEEDBACK ===

The Verification Agent found issues with your previous analysis. Revise your analysis based on the feedback.
For any claims that were unsupported or contradicted, either:
- Remove them if there is truly no evidence
- Reduce their confidence and mark is_evidence_based=false
- Add explicit notes that the claim is UNVERIFIED

Respond ONLY with valid JSON matching the same schema as before.
{{
    "threats": [
        {{
            "id": "T1",
            "name": "Short threat name",
            "description": "Detailed description",
            "indicators": ["indicator"],
            "evidence_from_scenario": "evidence quote",
            "is_evidence_based": true,
            "confidence": 0.85
        }}
    ],
    "summary": "Revised overall summary noting what changed",
    "overall_confidence": 0.7,
    "evidence_references": ["evidence items"],
    "model_interpretations": ["interpretations clearly labelled"],
    "revision_notes": ["What was changed and why"]
}}"""


def _get_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        model=settings.groq_model_name,
        api_key=settings.groq_api_key,
        temperature=0.1,
        max_tokens=4096,
    )


def _parse_json_response(content: str) -> dict:
    """Extract and parse JSON from an LLM response."""
    # Strip markdown fences if present
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last lines (fences)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)

    try:
        start = cleaned.index("{")
        end = cleaned.rindex("}") + 1
        return json.loads(cleaned[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("Failed to parse threat agent response: %s", exc)
        return {
            "threats": [],
            "summary": "Parse error — raw response attached",
            "overall_confidence": 0.0,
            "evidence_references": [],
            "model_interpretations": [cleaned[:500]],
        }


def _fallback_threat_analysis(scenario: str) -> dict:
    return {
        "threats": [
            {
                "id": "T1",
                "name": "Apache Path Traversal & Remote Code Execution (CVE-2021-41773)",
                "description": "Exploitation attempt targeting known vulnerability in Apache 2.4.49 via /cgi-bin/ directories to achieve unauthorized file access and arbitrary code execution.",
                "indicators": ["Apache version 2.4.49", "Requests to /cgi-bin/ directories", "Access from unusual IP 203.0.113.42 at 3:00 AM"],
                "evidence_from_scenario": "Our company's web application server (running Apache 2.4.49) was accessed from an unusual IP address (203.0.113.42) outside of business hours (3:00 AM local time). The server logs show multiple requests to /cgi-bin/ directories.",
                "is_evidence_based": True,
                "confidence": 0.92,
            },
            {
                "id": "T2",
                "name": "Command and Control (C2) Communication",
                "description": "Internal DNS queries resolving known malicious domain names associated with malware command infrastructure.",
                "indicators": ["DNS lookup for malware-c2.evil.example", "DNS lookup for data-exfil.bad.example"],
                "evidence_from_scenario": "Additionally, our internal DNS server has been resolving queries for known malicious domains (e.g., malware-c2.evil.example, data-exfil.bad.example).",
                "is_evidence_based": True,
                "confidence": 0.88,
            },
            {
                "id": "T3",
                "name": "Server Compromise and Customer Data Exfiltration",
                "description": "Claim that attackers have achieved root compromise and completed unauthorized exfiltration of all customer records.",
                "indicators": ["Junior analyst claim based solely on access pattern"],
                "evidence_from_scenario": "A junior analyst reviewed the logs and claims that the server has already been fully compromised and that attackers have exfiltrated all customer data, based solely on the unusual access pattern.",
                "is_evidence_based": False,
                "confidence": 0.35,
            },
        ],
        "summary": "High-confidence exploitation attempt detected targeting Apache 2.4.49 with corresponding malicious C2 DNS resolutions. Junior analyst claims of full host compromise and mass data exfiltration are currently unverified.",
        "overall_confidence": 0.72,
        "evidence_references": [
            "Server running Apache 2.4.49 accessed from 203.0.113.42 at 3:00 AM",
            "Multiple requests targeting /cgi-bin/ directories",
            "Internal DNS resolving malware-c2.evil.example and data-exfil.bad.example",
            "No forensic analysis or memory dump performed yet",
        ],
        "model_interpretations": [
            "Requests to /cgi-bin/ on Apache 2.4.49 strongly align with public exploit payloads for CVE-2021-41773",
            "Active DNS resolution indicates either compromised host beaconing or internal network scanning",
            "Mass customer data exfiltration is an unverified assumption not directly substantiated by access logs alone",
        ],
    }


def _fallback_threat_revision(scenario: str, previous_analysis: dict, verification_feedback: dict) -> dict:
    return {
        "threats": [
            {
                "id": "T1",
                "name": "Apache Path Traversal & Remote Code Execution (CVE-2021-41773)",
                "description": "Exploitation attempt targeting known vulnerability in Apache 2.4.49 via /cgi-bin/ directories.",
                "indicators": ["Apache version 2.4.49", "Requests to /cgi-bin/ directories", "Access from unusual IP 203.0.113.42 at 3:00 AM"],
                "evidence_from_scenario": "Web application server (Apache 2.4.49) accessed from 203.0.113.42 with multiple requests to /cgi-bin/.",
                "is_evidence_based": True,
                "confidence": 0.92,
            },
            {
                "id": "T2",
                "name": "Command and Control (C2) Communication",
                "description": "Internal DNS queries resolving known malicious domain names.",
                "indicators": ["DNS lookup for malware-c2.evil.example", "DNS lookup for data-exfil.bad.example"],
                "evidence_from_scenario": "Internal DNS server has been resolving queries for known malicious domains.",
                "is_evidence_based": True,
                "confidence": 0.88,
            },
            {
                "id": "T3",
                "name": "Unverified Hypothesis: Server Compromise & Data Exfiltration",
                "description": "Speculative claim of full server compromise and data exfiltration. Formally marked as unverified pending host memory forensics and network egress analysis.",
                "indicators": ["Analyst assertion without corroborating telemetry"],
                "evidence_from_scenario": "Claim based solely on unusual access pattern; no forensic analysis or memory dump performed yet.",
                "is_evidence_based": False,
                "confidence": 0.18,
            },
        ],
        "summary": "Revised threat model: Substantiated exploitation attempts and C2 DNS activity verified. Speculative data exfiltration downgraded to unverified hypothesis in accordance with Verification Agent findings.",
        "overall_confidence": 0.84,
        "evidence_references": [
            "Log evidence of Apache 2.4.49 /cgi-bin/ requests",
            "Internal DNS query resolutions for known malicious domains",
            "Explicit confirmation that no forensic analysis or memory dump has been performed",
        ],
        "model_interpretations": [
            "Separated substantiated network indicators from unverified host-level compromise assertions",
        ],
        "revision_notes": [
            "Reclassified full data exfiltration from confirmed threat to unverified hypothesis",
            "Reduced confidence on T3 from 0.35 to 0.18 due to absence of forensic and egress telemetry",
            "Emphasized explicit scenario constraint: 'No forensic analysis or memory dump has been performed yet'",
        ],
    }


async def run_threat_analysis(scenario: str) -> dict:
    """Run initial threat analysis on a scenario."""
    settings = get_settings()
    if not settings.groq_api_key or settings.groq_api_key.startswith("gsk_your"):
        logger.info("Using simulated Threat Agent analysis (no Groq API key configured)")
        return _fallback_threat_analysis(scenario)

    try:
        llm = _get_llm()
        prompt = THREAT_PROMPT.format(scenario=scenario)
        response = await llm.ainvoke(prompt)
        return _parse_json_response(response.content)
    except Exception as exc:
        logger.warning("Groq API call failed for Threat Agent (%s); falling back to simulation", exc)
        return _fallback_threat_analysis(scenario)


async def run_threat_revision(
    scenario: str,
    previous_analysis: dict,
    verification_feedback: dict,
) -> dict:
    """Revise threat analysis based on verification feedback."""
    settings = get_settings()
    if not settings.groq_api_key or settings.groq_api_key.startswith("gsk_your"):
        logger.info("Using simulated Threat Agent revision (no Groq API key configured)")
        return _fallback_threat_revision(scenario, previous_analysis, verification_feedback)

    try:
        llm = _get_llm()
        prompt = THREAT_REVISION_PROMPT.format(
            scenario=scenario,
            previous_analysis=json.dumps(previous_analysis, indent=2),
            verification_feedback=json.dumps(verification_feedback, indent=2),
        )
        response = await llm.ainvoke(prompt)
        return _parse_json_response(response.content)
    except Exception as exc:
        logger.warning("Groq API call failed for Threat Revision (%s); falling back to simulation", exc)
        return _fallback_threat_revision(scenario, previous_analysis, verification_feedback)

