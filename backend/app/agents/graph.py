"""LangGraph orchestration — wires the three agents into a state graph with real execution traces."""

import json
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, END

from app.agents.threat_agent import run_threat_analysis, run_threat_revision
from app.agents.risk_agent import run_risk_assessment, run_risk_revision
from app.agents.verification_agent import run_verification

logger = logging.getLogger(__name__)


# ── State schema ────────────────────────────────────────────────────

class AgentState(TypedDict):
    """Shared state flowing through the graph."""
    scenario: str
    # Stage 1 outputs
    initial_threat_analysis: dict
    initial_risk_assessment: dict
    verification_result: dict
    # Stage 2 outputs
    revised_threat_analysis: dict
    revised_risk_assessment: dict
    # Final
    final_assessment: dict
    needs_revision: bool
    # Trace
    execution_trace: Annotated[list, operator.add]
    graph_edges: Annotated[list, operator.add]


# ── Helper ──────────────────────────────────────────────────────────

def _trace_entry(
    agent: str, stage: str, order: int,
    input_summary: str, output_summary: str,
    duration_ms: float,
) -> dict:
    return {
        "agent_name": agent,
        "step_order": order,
        "stage": stage,
        "input_summary": input_summary,
        "output_summary": output_summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_ms": round(duration_ms, 1),
    }


def _edge(source: str, target: str, label: str, data: str = "") -> dict:
    return {"source": source, "target": target, "label": label, "data_passed": data}


# ── Node functions ──────────────────────────────────────────────────

async def threat_analysis_node(state: AgentState) -> dict:
    """Stage 1 — Threat Agent identifies threats."""
    logger.info("▶ Threat Agent: starting analysis")
    t0 = time.perf_counter()

    result = await run_threat_analysis(state["scenario"])
    elapsed = (time.perf_counter() - t0) * 1000

    summary = result.get("summary", "")[:200]
    n_threats = len(result.get("threats", []))

    return {
        "initial_threat_analysis": result,
        "execution_trace": [
            _trace_entry(
                "Threat Agent", "initial", 1,
                f"Scenario ({len(state['scenario'])} chars)",
                f"Identified {n_threats} threats — {summary}",
                elapsed,
            )
        ],
        "graph_edges": [
            _edge("scenario_input", "threat_agent", "scenario text",
                  f"{len(state['scenario'])} chars"),
        ],
    }


async def risk_assessment_node(state: AgentState) -> dict:
    """Stage 1 — Risk Agent assesses severity."""
    logger.info("▶ Risk Agent: assessing risk")
    t0 = time.perf_counter()

    result = await run_risk_assessment(
        state["scenario"],
        state["initial_threat_analysis"],
    )
    elapsed = (time.perf_counter() - t0) * 1000

    severity = result.get("severity", "Unknown")
    score = result.get("risk_score", 0)

    return {
        "initial_risk_assessment": result,
        "execution_trace": [
            _trace_entry(
                "Risk Agent", "initial", 2,
                f"Scenario + {len(state['initial_threat_analysis'].get('threats', []))} threats",
                f"Severity={severity}, Score={score}/10",
                elapsed,
            )
        ],
        "graph_edges": [
            _edge("threat_agent", "risk_agent", "threat analysis",
                  f"{len(state['initial_threat_analysis'].get('threats', []))} threats"),
        ],
    }


async def verification_node(state: AgentState) -> dict:
    """Stage 1 — Verification Agent checks claims."""
    logger.info("▶ Verification Agent: checking claims")
    t0 = time.perf_counter()

    result = await run_verification(
        state["scenario"],
        state["initial_threat_analysis"],
        state["initial_risk_assessment"],
    )
    elapsed = (time.perf_counter() - t0) * 1000

    status = result.get("overall_status", "unknown")
    unsupported = len(result.get("unsupported_claims", []))
    contradictions = len(result.get("contradictions", []))
    needs_rev = status == "needs_revision"

    return {
        "verification_result": result,
        "needs_revision": needs_rev,
        "execution_trace": [
            _trace_entry(
                "Verification Agent", "initial", 3,
                "Threat analysis + Risk assessment",
                f"Status={status}, Unsupported={unsupported}, Contradictions={contradictions}",
                elapsed,
            )
        ],
        "graph_edges": [
            _edge("risk_agent", "verification_agent", "risk assessment",
                  f"Severity={state['initial_risk_assessment'].get('severity', '?')}"),
        ],
    }


async def revision_node(state: AgentState) -> dict:
    """Stage 2 — Agents revise based on verification feedback."""
    logger.info("▶ Revision: threat & risk agents revising")
    t0 = time.perf_counter()

    # Revise threat analysis
    revised_threats = await run_threat_revision(
        state["scenario"],
        state["initial_threat_analysis"],
        state["verification_result"],
    )
    t_mid = time.perf_counter()

    # Revise risk assessment
    revised_risk = await run_risk_revision(
        state["scenario"],
        revised_threats,
        state["initial_risk_assessment"],
        state["verification_result"],
    )
    elapsed = (time.perf_counter() - t0) * 1000
    threat_elapsed = (t_mid - t0) * 1000
    risk_elapsed = elapsed - threat_elapsed

    return {
        "revised_threat_analysis": revised_threats,
        "revised_risk_assessment": revised_risk,
        "execution_trace": [
            _trace_entry(
                "Threat Agent", "revision", 4,
                "Original analysis + Verification feedback",
                f"Revised: {len(revised_threats.get('revision_notes', []))} changes",
                threat_elapsed,
            ),
            _trace_entry(
                "Risk Agent", "revision", 5,
                "Revised threats + Verification feedback",
                f"Revised severity={revised_risk.get('severity', '?')}, score={revised_risk.get('risk_score', '?')}",
                risk_elapsed,
            ),
        ],
        "graph_edges": [
            _edge("verification_agent", "threat_agent_revision",
                  "correction requests",
                  f"{len(state['verification_result'].get('corrections_requested', []))} corrections"),
            _edge("threat_agent_revision", "risk_agent_revision",
                  "revised threats", ""),
        ],
    }


async def final_assessment_node(state: AgentState) -> dict:
    """Produce the final combined assessment."""
    logger.info("▶ Final assessment")
    t0 = time.perf_counter()

    # Use revised outputs if available, otherwise initial
    threat = state.get("revised_threat_analysis") or state.get("initial_threat_analysis", {})
    risk = state.get("revised_risk_assessment") or state.get("initial_risk_assessment", {})
    verification = state.get("verification_result", {})

    # Count changes
    initial_unsupported = len(verification.get("unsupported_claims", []))
    revised_threats = state.get("revised_threat_analysis", {})
    revision_happened = bool(revised_threats)

    # Build before/after comparison
    before_after = {
        "initial_severity": state.get("initial_risk_assessment", {}).get("severity", "Unknown"),
        "final_severity": risk.get("severity", "Unknown"),
        "initial_risk_score": state.get("initial_risk_assessment", {}).get("risk_score", 0),
        "final_risk_score": risk.get("risk_score", 0),
        "initial_confidence": state.get("initial_risk_assessment", {}).get("confidence", 0),
        "final_confidence": risk.get("confidence", 0),
        "unsupported_claims_found": initial_unsupported,
        "revision_performed": revision_happened,
        "initial_threat_count": len(state.get("initial_threat_analysis", {}).get("threats", [])),
        "final_threat_count": len(threat.get("threats", [])),
    }

    final = {
        "severity": risk.get("severity", "Unknown"),
        "risk_score": risk.get("risk_score", 0),
        "confidence": risk.get("confidence", 0),
        "summary": risk.get("reasoning", ""),
        "threats": threat.get("threats", []),
        "evidence": risk.get("evidence", []),
        "recommendations": risk.get("recommendations", []),
        "verification_status": verification.get("overall_status", "unknown"),
        "before_after": before_after,
        "disclaimer": (
            "This assessment is AI-generated and may contain errors. "
            "Evidence checks reduce but cannot eliminate unsupported claims. "
            "Always verify critical findings with qualified security professionals."
        ),
    }

    elapsed = (time.perf_counter() - t0) * 1000

    edge_source = "risk_agent_revision" if revision_happened else "verification_agent"

    return {
        "final_assessment": final,
        "execution_trace": [
            _trace_entry(
                "Final Assessment", "final", 6,
                "All agent outputs",
                f"Final severity={final['severity']}, score={final['risk_score']}",
                elapsed,
            )
        ],
        "graph_edges": [
            _edge(edge_source, "final_assessment", "combined output", ""),
        ],
    }


# ── Routing ─────────────────────────────────────────────────────────

def should_revise(state: AgentState) -> str:
    """Decide whether to revise or go straight to final."""
    if state.get("needs_revision", False):
        logger.info("↻ Verification found issues — routing to revision")
        return "revision"
    logger.info("✓ Verification passed — routing to final")
    return "finalize_assessment"


# ── Build the graph ─────────────────────────────────────────────────

def build_graph():
    """Construct and compile the LangGraph state graph."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("threat_analysis", threat_analysis_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("verification", verification_node)
    workflow.add_node("revision", revision_node)
    workflow.add_node("finalize_assessment", final_assessment_node)

    # Set edges
    workflow.set_entry_point("threat_analysis")
    workflow.add_edge("threat_analysis", "risk_assessment")
    workflow.add_edge("risk_assessment", "verification")
    workflow.add_conditional_edges(
        "verification",
        should_revise,
        {"revision": "revision", "finalize_assessment": "finalize_assessment"},
    )
    workflow.add_edge("revision", "finalize_assessment")
    workflow.add_edge("finalize_assessment", END)

    return workflow.compile()


async def run_assessment_pipeline(scenario: str) -> dict:
    """Run the full multi-agent assessment pipeline and return complete results."""
    graph = build_graph()

    initial_state: AgentState = {
        "scenario": scenario,
        "initial_threat_analysis": {},
        "initial_risk_assessment": {},
        "verification_result": {},
        "revised_threat_analysis": {},
        "revised_risk_assessment": {},
        "final_assessment": {},
        "needs_revision": False,
        "execution_trace": [],
        "graph_edges": [],
    }

    # Run the graph
    result = await graph.ainvoke(initial_state)

    return {
        "id": str(uuid.uuid4()),
        "scenario": scenario,
        "initial_threat_analysis": result.get("initial_threat_analysis", {}),
        "initial_risk_assessment": result.get("initial_risk_assessment", {}),
        "verification_result": result.get("verification_result", {}),
        "revised_threat_analysis": result.get("revised_threat_analysis", {}),
        "revised_risk_assessment": result.get("revised_risk_assessment", {}),
        "final_assessment": result.get("final_assessment", {}),
        "execution_trace": result.get("execution_trace", []),
        "graph_edges": result.get("graph_edges", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
