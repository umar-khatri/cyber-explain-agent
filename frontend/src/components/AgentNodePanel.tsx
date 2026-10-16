"use client";

import type { AssessmentResult } from "@/types";

interface Props {
  assessment: AssessmentResult;
  selectedNodeId: string | null;
  onClose: () => void;
}

export default function AgentNodePanel({
  assessment,
  selectedNodeId,
  onClose,
}: Props) {
  if (!selectedNodeId) return null;

  const nodeData = getNodeData(assessment, selectedNodeId);
  if (!nodeData) return null;

  return (
    <div className="cyber-card glow-purple overflow-y-auto max-h-[70vh]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-bold text-base">{nodeData.title}</h3>
          <span className={`badge badge-${nodeData.stageBadge} mt-1`}>
            {nodeData.stageLabel}
          </span>
        </div>
        <button onClick={onClose} className="btn-secondary !p-2 !rounded-lg">
          ✕
        </button>
      </div>

      {/* Input */}
      <Section title="📥 Input" className="mb-4">
        <p className="text-sm text-[var(--color-cyber-text-dim)]">
          {nodeData.input}
        </p>
      </Section>

      {/* Conclusion / Output */}
      {nodeData.conclusion && (
        <Section title="📊 Conclusion" className="mb-4">
          <p className="text-sm">{nodeData.conclusion}</p>
        </Section>
      )}

      {/* Confidence */}
      {nodeData.confidence !== undefined && (
        <Section title="📈 Confidence" className="mb-4">
          <div className="confidence-bar">
            <div
              className="confidence-bar-fill"
              style={{
                width: `${nodeData.confidence * 100}%`,
                background:
                  nodeData.confidence > 0.7
                    ? "var(--color-cyber-green)"
                    : nodeData.confidence > 0.4
                    ? "var(--color-cyber-orange)"
                    : "var(--color-cyber-red)",
              }}
            />
          </div>
          <p className="text-xs text-[var(--color-cyber-text-dim)] mt-1">
            {(nodeData.confidence * 100).toFixed(0)}%
          </p>
        </Section>
      )}

      {/* Evidence References */}
      {nodeData.evidence.length > 0 && (
        <Section title="🔍 Evidence (from scenario)" className="mb-4">
          <ul className="space-y-1">
            {nodeData.evidence.map((e, i) => (
              <li
                key={i}
                className="text-sm text-emerald-400 bg-emerald-500/5 border border-emerald-500/20 rounded-lg px-3 py-2"
              >
                <span className="font-medium text-emerald-300">Evidence:</span>{" "}
                {e}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Model Interpretations */}
      {nodeData.interpretations.length > 0 && (
        <Section
          title="🤖 Model Interpretations (not direct evidence)"
          className="mb-4"
        >
          <ul className="space-y-1">
            {nodeData.interpretations.map((interp, i) => (
              <li
                key={i}
                className="text-sm text-amber-400 bg-amber-500/5 border border-amber-500/20 rounded-lg px-3 py-2"
              >
                <span className="font-medium text-amber-300">
                  Interpretation:
                </span>{" "}
                {interp}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Output details */}
      {nodeData.details.length > 0 && (
        <Section title="📋 Details">
          <div className="space-y-2">
            {nodeData.details.map((d, i) => (
              <div
                key={i}
                className="text-sm bg-[var(--color-cyber-bg)] rounded-lg p-3 border border-[var(--color-cyber-border)]"
              >
                <p className="font-medium text-[var(--color-cyber-accent)] mb-1">
                  {d.label}
                </p>
                <p className="text-[var(--color-cyber-text-dim)]">{d.value}</p>
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}

function Section({
  title,
  className = "",
  children,
}: {
  title: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={className}>
      <h4 className="text-xs font-semibold text-[var(--color-cyber-text-dim)] uppercase tracking-wider mb-2">
        {title}
      </h4>
      {children}
    </div>
  );
}

/* ── Extract node-specific data ── */

interface NodeInfo {
  title: string;
  stageLabel: string;
  stageBadge: string;
  input: string;
  conclusion: string;
  confidence?: number;
  evidence: string[];
  interpretations: string[];
  details: { label: string; value: string }[];
}

function getNodeData(
  a: AssessmentResult,
  nodeId: string
): NodeInfo | null {
  switch (nodeId) {
    case "scenario_input":
      return {
        title: "Scenario Input",
        stageLabel: "Input",
        stageBadge: "medium",
        input: "User-provided cybersecurity scenario",
        conclusion: a.scenario,
        evidence: [],
        interpretations: [],
        details: [
          { label: "Characters", value: `${a.scenario.length}` },
        ],
      };

    case "threat_agent": {
      const ta = a.initial_threat_analysis;
      return {
        title: "Threat Agent — Initial",
        stageLabel: "Stage 1: Initial",
        stageBadge: "medium",
        input: "Cybersecurity scenario text",
        conclusion: ta?.summary || "No summary",
        confidence: ta?.overall_confidence,
        evidence: ta?.evidence_references || [],
        interpretations: ta?.model_interpretations || [],
        details: (ta?.threats || []).map((t) => ({
          label: `${t.id}: ${t.name} (${t.is_evidence_based ? "Evidence-based" : "⚠️ Interpretation"})`,
          value: `${t.description}\nConfidence: ${(t.confidence * 100).toFixed(0)}%\nEvidence: ${t.evidence_from_scenario || "None cited"}`,
        })),
      };
    }

    case "risk_agent": {
      const ra = a.initial_risk_assessment;
      return {
        title: "Risk Agent — Initial",
        stageLabel: "Stage 1: Initial",
        stageBadge: "medium",
        input: "Scenario + Threat analysis",
        conclusion: ra?.reasoning || "No reasoning",
        confidence: ra?.confidence,
        evidence: ra?.evidence || [],
        interpretations: ra?.model_interpretations || [],
        details: [
          { label: "Severity", value: ra?.severity || "Unknown" },
          { label: "Risk Score", value: `${ra?.risk_score || 0}/10` },
          ...(ra?.recommendations || []).map((r, i) => ({
            label: `Recommendation ${i + 1}`,
            value: r,
          })),
        ],
      };
    }

    case "verification_agent": {
      const vr = a.verification_result;
      return {
        title: "Verification Agent",
        stageLabel: `Status: ${vr?.overall_status || "unknown"}`,
        stageBadge: vr?.overall_status || "medium",
        input: "Threat analysis + Risk assessment",
        conclusion: vr?.explanation || "No explanation",
        confidence: vr?.evidence_quality_score,
        evidence: (vr?.supported_claims || []).map(
          (c) => `✓ ${c.claim}: ${c.explanation}`
        ),
        interpretations: (vr?.unsupported_claims || []).map(
          (c) => `⚠️ UNSUPPORTED — ${c.claim}: ${c.explanation}`
        ),
        details: [
          {
            label: "Claims Checked",
            value: `${vr?.total_claims_checked || 0} total — ${vr?.supported_count || 0} supported, ${vr?.unsupported_count || 0} unsupported, ${vr?.contradicted_count || 0} contradicted`,
          },
          ...(vr?.corrections_requested || []).map((c, i) => ({
            label: `Correction ${i + 1}`,
            value: c,
          })),
          ...(vr?.contradictions || []).map((c) => ({
            label: `🚫 Contradiction`,
            value: `${c.claim} — ${c.explanation}`,
          })),
          ...(vr?.disagreements || []).map((d) => ({
            label: `⚔️ Disagreement: ${d.topic}`,
            value: `Threat Agent: ${d.threat_agent_position}\nRisk Agent: ${d.risk_agent_position}\nEvidence: ${d.evidence_assessment}`,
          })),
        ],
      };
    }

    case "threat_agent_revision": {
      const rt = a.revised_threat_analysis;
      return {
        title: "Threat Agent — Revised",
        stageLabel: "Stage 2: Revision",
        stageBadge: "high",
        input: "Original analysis + Verification feedback",
        conclusion: rt?.summary || "No summary",
        confidence: rt?.overall_confidence,
        evidence: rt?.evidence_references || [],
        interpretations: rt?.model_interpretations || [],
        details: [
          ...(rt?.revision_notes || []).map((n, i) => ({
            label: `Change ${i + 1}`,
            value: n,
          })),
          ...(rt?.threats || []).map((t) => ({
            label: `${t.id}: ${t.name} (${t.is_evidence_based ? "Evidence-based" : "⚠️ Interpretation"})`,
            value: `${t.description}\nConfidence: ${(t.confidence * 100).toFixed(0)}%`,
          })),
        ],
      };
    }

    case "risk_agent_revision": {
      const rr = a.revised_risk_assessment;
      return {
        title: "Risk Agent — Revised",
        stageLabel: "Stage 2: Revision",
        stageBadge: "high",
        input: "Revised threats + Verification feedback",
        conclusion: rr?.reasoning || "No reasoning",
        confidence: rr?.confidence,
        evidence: rr?.evidence || [],
        interpretations: rr?.model_interpretations || [],
        details: [
          { label: "Severity", value: rr?.severity || "Unknown" },
          { label: "Risk Score", value: `${rr?.risk_score || 0}/10` },
          ...(rr?.revision_notes || []).map((n, i) => ({
            label: `Change ${i + 1}`,
            value: n,
          })),
        ],
      };
    }

    case "final_assessment": {
      const fa = a.final_assessment;
      return {
        title: "Final Assessment",
        stageLabel: `Verification: ${fa?.verification_status || "unknown"}`,
        stageBadge: fa?.verification_status === "verified" ? "verified" : "needs_revision",
        input: "All agent outputs (revised if applicable)",
        conclusion: fa?.summary || "No summary",
        confidence: fa?.confidence,
        evidence: fa?.evidence || [],
        interpretations: [],
        details: [
          { label: "Final Severity", value: fa?.severity || "Unknown" },
          { label: "Final Risk Score", value: `${fa?.risk_score || 0}/10` },
          ...(fa?.recommendations || []).map((r, i) => ({
            label: `Recommendation ${i + 1}`,
            value: r,
          })),
          { label: "⚠️ Disclaimer", value: fa?.disclaimer || "" },
        ],
      };
    }

    default:
      return null;
  }
}
