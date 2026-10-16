"""Pydantic models for API requests, responses, and internal data structures."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---------- Request models ----------

class ScenarioRequest(BaseModel):
    """User-submitted cybersecurity scenario."""
    scenario: str = Field(..., min_length=10, description="The cybersecurity scenario to analyse")


# ---------- Agent output models ----------

class ThreatItem(BaseModel):
    id: str
    name: str
    description: str
    indicators: list[str] = []
    evidence_from_scenario: str = ""
    is_evidence_based: bool = True
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class ThreatAnalysis(BaseModel):
    model_config = {"protected_namespaces": ()}
    threats: list[ThreatItem] = []
    summary: str = ""
    overall_confidence: float = Field(0.5, ge=0.0, le=1.0)
    evidence_references: list[str] = []
    model_interpretations: list[str] = []


class RiskAssessment(BaseModel):
    model_config = {"protected_namespaces": ()}
    severity: str = "Medium"  # Critical, High, Medium, Low
    risk_score: float = Field(5.0, ge=0.0, le=10.0)
    evidence: list[str] = []
    reasoning: str = ""
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    model_interpretations: list[str] = []
    recommendations: list[str] = []


class ClaimCheck(BaseModel):
    claim: str
    status: str  # "supported", "unsupported", "contradicted"
    evidence: str = ""
    explanation: str = ""


class VerificationResult(BaseModel):
    supported_claims: list[ClaimCheck] = []
    unsupported_claims: list[ClaimCheck] = []
    contradictions: list[ClaimCheck] = []
    corrections_requested: list[str] = []
    overall_status: str = "pending"
    explanation: str = ""


# ---------- Execution trace ----------

class TraceStep(BaseModel):
    agent_name: str
    step_order: int
    stage: str  # "initial" or "revision"
    input_summary: str
    output_summary: str
    timestamp: str
    duration_ms: float = 0.0


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str = ""
    data_passed: str = ""


# ---------- Full assessment response ----------

class AssessmentResponse(BaseModel):
    id: str
    scenario: str
    initial_threat_analysis: Optional[dict] = None
    initial_risk_assessment: Optional[dict] = None
    verification_result: Optional[dict] = None
    revised_threat_analysis: Optional[dict] = None
    revised_risk_assessment: Optional[dict] = None
    final_assessment: Optional[dict] = None
    execution_trace: list[dict] = []
    graph_edges: list[dict] = []
    created_at: str = ""


class AssessmentListItem(BaseModel):
    id: str
    scenario: str
    severity: str = ""
    created_at: str = ""
