"""Risk Assessment Agent — evaluates severity and provides evidence-based reasoning."""

import json
import logging
from langchain_groq import ChatGroq
from app.config import get_settings

logger = logging.getLogger(__name__)

RISK_PROMPT = """You are a Cybersecurity Risk Assessment Agent.

Given the scenario and the Threat Agent's analysis, assess the overall risk severity and provide evidence-based reasoning.

=== SCENARIO ===
{scenario}
=== END SCENARIO ===

=== THREAT ANALYSIS ===
{threat_analysis}
=== END THREAT ANALYSIS ===

Respond ONLY with valid JSON (no markdown, no commentary):
{{
    "severity": "Critical|High|Medium|Low",
    "risk_score": 7.5,
    "evidence": [
        "Evidence item 1 directly from the scenario or threat analysis"
    ],
    "reasoning": "Step-by-step explanation of how you arrived at this severity rating, referencing specific evidence",
    "confidence": 0.8,
    "model_interpretations": [
        "Any conclusions that go beyond the directly stated evidence"
    ],
    "recommendations": [
        "Actionable recommendation 1"
    ],
    "risk_factors": [
        {{
            "factor": "Factor name",
            "impact": "High|Medium|Low",
            "evidence": "Supporting evidence",
            "is_evidence_based": true
        }}
    ]
}}

RULES:
1. Base your severity assessment primarily on EVIDENCE, not assumptions.
2. Clearly separate evidence-based conclusions from model interpretations.
3. If the threat analysis contains claims marked as not evidence-based, factor that uncertainty into your risk score.
4. Confidence should reflect the strength of available evidence.
5. Do NOT inflate severity beyond what the evidence supports."""


RISK_REVISION_PROMPT = """You are a Cybersecurity Risk Assessment Agent revising your previous assessment.

=== ORIGINAL SCENARIO ===
{scenario}
=== END SCENARIO ===

=== REVISED THREAT ANALYSIS ===
{revised_threat_analysis}
=== END REVISED THREAT ANALYSIS ===

=== YOUR PREVIOUS ASSESSMENT ===
{previous_assessment}
=== END PREVIOUS ASSESSMENT ===

=== VERIFICATION FEEDBACK ===
{verification_feedback}
=== END VERIFICATION FEEDBACK ===

Revise your risk assessment based on the verification feedback and the revised threat analysis.
For any risk factors based on unsupported claims:
- Lower their impact or remove them
- Adjust the overall risk score accordingly
- Clearly note what changed

Respond ONLY with valid JSON using the same schema, adding a "revision_notes" field:
{{
    "severity": "Critical|High|Medium|Low",
    "risk_score": 6.0,
    "evidence": ["evidence items"],
    "reasoning": "Revised reasoning",
    "confidence": 0.7,
    "model_interpretations": ["interpretations"],
    "recommendations": ["recommendations"],
    "risk_factors": [
        {{
            "factor": "Factor name",
            "impact": "High|Medium|Low",
            "evidence": "Supporting evidence",
            "is_evidence_based": true
        }}
    ],
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
        logger.warning("Failed to parse risk agent response: %s", exc)
        return {
            "severity": "Unknown",
            "risk_score": 0.0,
            "evidence": [],
            "reasoning": "Parse error — raw response attached",
            "confidence": 0.0,
            "model_interpretations": [cleaned[:500]],
            "recommendations": [],
        }


def _fallback_risk_assessment(scenario: str, threat_analysis: dict) -> dict:
    return {
        "severity": "Critical",
        "risk_score": 9.0,
        "evidence": [
            "Access from untrusted external IP (203.0.113.42) at 3:00 AM",
            "Targeting known vulnerable web server: Apache 2.4.49 with requests to /cgi-bin/",
            "Internal DNS resolving known malicious C2 domains (malware-c2.evil.example, data-exfil.bad.example)",
            "Analyst report claiming complete server compromise and customer data exfiltration",
        ],
        "reasoning": "Initial assessment accepts the junior analyst's claim of customer data exfiltration at face value alongside confirmed Apache 2.4.49 path traversal attempts and active C2 beaconing. The combination of root compromise and data loss warrants a Critical severity rating.",
        "confidence": 0.65,
        "model_interpretations": [
            "Assuming full server compromise based on the presence of unusual access patterns",
            "Assuming sensitive customer data was accessed and successfully exfiltrated",
            "Potential high regulatory exposure (GDPR/CCPA notifications required)",
        ],
        "recommendations": [
            "Immediately isolate the web server from the internal production network",
            "Capture forensic volatile memory dump and disk image before rebooting",
            "Block IP 203.0.113.42 and sinkhole malicious C2 domains across all DNS resolvers",
            "Initiate incident response protocol for suspected data breach",
        ],
        "risk_factors": [
            {"factor": "Known Remote Code Execution Vector (Apache 2.4.49)", "impact": "High", "evidence": "Apache 2.4.49 with /cgi-bin/ requests", "is_evidence_based": True},
            {"factor": "Active C2 Communication", "impact": "High", "evidence": "DNS queries for malware-c2.evil.example", "is_evidence_based": True},
            {"factor": "Total Customer Data Exfiltration", "impact": "Critical", "evidence": "Junior analyst assumption; unverified", "is_evidence_based": False},
        ],
    }


def _fallback_risk_revision(
    scenario: str,
    revised_threat_analysis: dict,
    previous_assessment: dict,
    verification_feedback: dict,
) -> dict:
    return {
        "severity": "High",
        "risk_score": 7.6,
        "evidence": [
            "Unauthorized access from 203.0.113.42 at 3:00 AM",
            "Exploit probes targeting Apache 2.4.49 /cgi-bin/ directories",
            "Active DNS resolutions for malicious C2 domains",
            "Confirmed: No forensic analysis or memory dump has been performed yet",
        ],
        "reasoning": "Severity revised from Critical to High. The server exhibits confirmed indicators of exploitation attempts and malicious C2 network activity; however, the claim of full compromise and customer data exfiltration lacks forensic or egress data. Downgraded to reflect verified risk while prioritizing forensic evidence collection.",
        "confidence": 0.88,
        "model_interpretations": [
            "Attacker was in the reconnaissance / initial exploitation phase",
            "Exfiltration remains an unproven risk until network egress bandwidth and host memory are audited",
        ],
        "recommendations": [
            "Keep server isolated on perimeter VLAN while preserving volatile memory",
            "Perform immediate memory dump and inspect running processes for web shells",
            "Audit firewall and NetFlow logs for anomalous outbound byte transfers during the 3:00 AM window",
            "Upgrade Apache HTTP Server to a patched release (2.4.51+) to eliminate CVE-2021-41773",
        ],
        "risk_factors": [
            {"factor": "Vulnerability Exploitation Probe (Apache 2.4.49)", "impact": "High", "evidence": "Apache 2.4.49 with /cgi-bin/ requests", "is_evidence_based": True},
            {"factor": "Malicious C2 DNS Activity", "impact": "High", "evidence": "DNS resolution for malware-c2.evil.example", "is_evidence_based": True},
            {"factor": "Customer Data Exfiltration", "impact": "Medium", "evidence": "Hypothesis only; no egress logs or memory artifacts", "is_evidence_based": False},
        ],
        "revision_notes": [
            "Severity downgraded from Critical (9.0) to High (7.6) following Verification Agent critique",
            "Confidence increased from 0.65 to 0.88 by eliminating ungrounded data exfiltration assumptions",
            "Distinguished verified perimeter exploit probes from unverified host-level data exfiltration",
        ],
    }


async def run_risk_assessment(scenario: str, threat_analysis: dict) -> dict:
    """Run initial risk assessment based on scenario and threat analysis."""
    settings = get_settings()
    if not settings.groq_api_key or settings.groq_api_key.startswith("gsk_your"):
        logger.info("Using simulated Risk Agent assessment (no Groq API key configured)")
        return _fallback_risk_assessment(scenario, threat_analysis)

    try:
        llm = _get_llm()
        prompt = RISK_PROMPT.format(
            scenario=scenario,
            threat_analysis=json.dumps(threat_analysis, indent=2),
        )
        response = await llm.ainvoke(prompt)
        return _parse_json_response(response.content)
    except Exception as exc:
        logger.warning("Groq API call failed for Risk Agent (%s); falling back to simulation", exc)
        return _fallback_risk_assessment(scenario, threat_analysis)


async def run_risk_revision(
    scenario: str,
    revised_threat_analysis: dict,
    previous_assessment: dict,
    verification_feedback: dict,
) -> dict:
    """Revise risk assessment based on verification feedback."""
    settings = get_settings()
    if not settings.groq_api_key or settings.groq_api_key.startswith("gsk_your"):
        logger.info("Using simulated Risk Agent revision (no Groq API key configured)")
        return _fallback_risk_revision(
            scenario,
            revised_threat_analysis,
            previous_assessment,
            verification_feedback,
        )

    try:
        llm = _get_llm()
        prompt = RISK_REVISION_PROMPT.format(
            scenario=scenario,
            revised_threat_analysis=json.dumps(revised_threat_analysis, indent=2),
            previous_assessment=json.dumps(previous_assessment, indent=2),
            verification_feedback=json.dumps(verification_feedback, indent=2),
        )
        response = await llm.ainvoke(prompt)
        return _parse_json_response(response.content)
    except Exception as exc:
        logger.warning("Groq API call failed for Risk Revision (%s); falling back to simulation", exc)
        return _fallback_risk_revision(
            scenario,
            revised_threat_analysis,
            previous_assessment,
            verification_feedback,
        )

