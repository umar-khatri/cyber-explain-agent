"use client";

import type { AssessmentResult } from "@/types";

interface Props {
  assessment: AssessmentResult;
}

export default function StageComparison({ assessment }: Props) {
  const ba = assessment.final_assessment?.before_after;
  if (!ba) return null;

  const severityChanged = ba.initial_severity !== ba.final_severity;
  const scoreChanged = ba.initial_risk_score !== ba.final_risk_score;
  const confidenceChanged = ba.initial_confidence !== ba.final_confidence;
  const threatCountChanged = ba.initial_threat_count !== ba.final_threat_count;

  return (
    <div className="cyber-card">
      <h3 className="font-semibold text-base mb-1">
        📊 Before vs After Verification
      </h3>
      <p className="text-xs text-[var(--color-cyber-text-dim)] mb-4">
        Comparing initial assessment (Stage 1) with revised assessment (Stage 2)
        {!ba.revision_performed && " — No revision was needed"}
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Stage 1 */}
        <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
          <h4 className="font-semibold text-sm text-cyan-400 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-500" />
            Stage 1 — Initial Assessment
          </h4>
          <MetricRow label="Severity" value={ba.initial_severity} badge />
          <MetricRow
            label="Risk Score"
            value={`${ba.initial_risk_score}/10`}
          />
          <MetricRow
            label="Confidence"
            value={`${(ba.initial_confidence * 100).toFixed(0)}%`}
          />
          <MetricRow label="Threats" value={`${ba.initial_threat_count}`} />
          <MetricRow
            label="Unsupported Claims"
            value={`${ba.unsupported_claims_found}`}
            highlight={ba.unsupported_claims_found > 0}
          />
        </div>

        {/* Stage 2 */}
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
          <h4 className="font-semibold text-sm text-emerald-400 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            Stage 2 — After Verification
          </h4>
          <MetricRow
            label="Severity"
            value={ba.final_severity}
            badge
            changed={severityChanged}
          />
          <MetricRow
            label="Risk Score"
            value={`${ba.final_risk_score}/10`}
            changed={scoreChanged}
          />
          <MetricRow
            label="Confidence"
            value={`${(ba.final_confidence * 100).toFixed(0)}%`}
            changed={confidenceChanged}
          />
          <MetricRow
            label="Threats"
            value={`${ba.final_threat_count}`}
            changed={threatCountChanged}
          />
          <MetricRow
            label="Revision Performed"
            value={ba.revision_performed ? "Yes" : "No"}
          />
        </div>
      </div>

      {/* Change summary */}
      {ba.revision_performed && (
        <div className="mt-4 p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
          <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
            What Changed
          </h4>
          <ul className="space-y-1 text-sm text-[var(--color-cyber-text-dim)]">
            {severityChanged && (
              <li className="changed-highlight">
                Severity: <span className="text-cyan-400">{ba.initial_severity}</span> →{" "}
                <span className="text-emerald-400">{ba.final_severity}</span>
              </li>
            )}
            {scoreChanged && (
              <li className="changed-highlight">
                Risk Score: <span className="text-cyan-400">{ba.initial_risk_score}</span> →{" "}
                <span className="text-emerald-400">{ba.final_risk_score}</span>
              </li>
            )}
            {confidenceChanged && (
              <li className="changed-highlight">
                Confidence: <span className="text-cyan-400">{(ba.initial_confidence * 100).toFixed(0)}%</span> →{" "}
                <span className="text-emerald-400">{(ba.final_confidence * 100).toFixed(0)}%</span>
              </li>
            )}
            {threatCountChanged && (
              <li className="changed-highlight">
                Threat count: <span className="text-cyan-400">{ba.initial_threat_count}</span> →{" "}
                <span className="text-emerald-400">{ba.final_threat_count}</span>
              </li>
            )}
            {ba.unsupported_claims_found > 0 && (
              <li className="changed-highlight">
                <span className="text-amber-400">{ba.unsupported_claims_found}</span> unsupported
                claim(s) identified and addressed
              </li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

function MetricRow({
  label,
  value,
  badge = false,
  changed = false,
  highlight = false,
}: {
  label: string;
  value: string;
  badge?: boolean;
  changed?: boolean;
  highlight?: boolean;
}) {
  return (
    <div
      className={`flex items-center justify-between py-1.5 ${
        changed ? "changed-highlight rounded" : ""
      }`}
    >
      <span className="text-xs text-[var(--color-cyber-text-dim)]">{label}</span>
      {badge ? (
        <span className={`badge badge-${value.toLowerCase()}`}>{value}</span>
      ) : (
        <span
          className={`text-sm font-medium ${
            highlight ? "text-amber-400" : "text-[var(--color-cyber-text)]"
          } ${changed ? "text-emerald-400" : ""}`}
        >
          {value}
        </span>
      )}
    </div>
  );
}
