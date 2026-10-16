/* ── CyberExplain AI — shared TypeScript types ── */

export interface ThreatItem {
  id: string;
  name: string;
  description: string;
  indicators: string[];
  evidence_from_scenario: string;
  is_evidence_based: boolean;
  confidence: number;
}

export interface ThreatAnalysis {
  threats: ThreatItem[];
  summary: string;
  overall_confidence: number;
  evidence_references: string[];
  model_interpretations: string[];
  revision_notes?: string[];
}

export interface RiskFactor {
  factor: string;
  impact: string;
  evidence: string;
  is_evidence_based: boolean;
}

export interface RiskAssessment {
  severity: string;
  risk_score: number;
  evidence: string[];
  reasoning: string;
  confidence: number;
  model_interpretations: string[];
  recommendations: string[];
  risk_factors?: RiskFactor[];
  revision_notes?: string[];
}

export interface ClaimCheck {
  claim: string;
  status: string;
  evidence: string;
  explanation: string;
  source_agent?: string;
  missing_evidence?: string;
}

export interface Disagreement {
  topic: string;
  threat_agent_position: string;
  risk_agent_position: string;
  evidence_assessment: string;
}

export interface VerificationResult {
  supported_claims: ClaimCheck[];
  unsupported_claims: ClaimCheck[];
  contradictions: ClaimCheck[];
  corrections_requested: string[];
  disagreements?: Disagreement[];
  overall_status: string;
  explanation: string;
  evidence_quality_score?: number;
  total_claims_checked?: number;
  supported_count?: number;
  unsupported_count?: number;
  contradicted_count?: number;
}

export interface BeforeAfter {
  initial_severity: string;
  final_severity: string;
  initial_risk_score: number;
  final_risk_score: number;
  initial_confidence: number;
  final_confidence: number;
  unsupported_claims_found: number;
  revision_performed: boolean;
  initial_threat_count: number;
  final_threat_count: number;
}

export interface FinalAssessment {
  severity: string;
  risk_score: number;
  confidence: number;
  summary: string;
  threats: ThreatItem[];
  evidence: string[];
  recommendations: string[];
  verification_status: string;
  before_after: BeforeAfter;
  disclaimer: string;
}

export interface TraceStep {
  agent_name: string;
  step_order: number;
  stage: string;
  input_summary: string;
  output_summary: string;
  timestamp: string;
  duration_ms: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
  data_passed: string;
}

export interface AssessmentResult {
  id: string;
  scenario: string;
  initial_threat_analysis: ThreatAnalysis;
  initial_risk_assessment: RiskAssessment;
  verification_result: VerificationResult;
  revised_threat_analysis?: ThreatAnalysis;
  revised_risk_assessment?: RiskAssessment;
  final_assessment: FinalAssessment;
  execution_trace: TraceStep[];
  graph_edges: GraphEdge[];
  created_at: string;
}

export interface AssessmentListItem {
  id: string;
  scenario: string;
  severity: string;
  created_at: string;
}

/* ── Graph visualization node data ── */

export type AgentNodeType =
  | "scenario_input"
  | "threat_agent"
  | "risk_agent"
  | "verification_agent"
  | "threat_agent_revision"
  | "risk_agent_revision"
  | "final_assessment";

export interface AgentNodeData {
  [key: string]: unknown;
  id: AgentNodeType;
  label: string;
  stage: "input" | "initial" | "revision" | "final";
  agent?: string;
  input?: string;
  output?: Record<string, unknown>;
  confidence?: number;
  status?: string;
  active: boolean;
}

