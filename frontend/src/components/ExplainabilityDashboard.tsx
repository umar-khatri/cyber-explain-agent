"use client";

import type { AssessmentResult } from "@/types";

interface Props {
  assessment: AssessmentResult;
}

export default function ExplainabilityDashboard({ assessment }: Props) {
  const { final_assessment: fa, verification_result: vr } = assessment;

  return (
    <div className="space-y-6">
      {/* Top-level risk overview */}
      <div className="cyber-card glow-cyan">
        <h3 className="font-semibold text-base mb-4">
          🛡️ Risk Assessment Overview
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            label="Severity"
            value={fa?.severity || "—"}
            color={severityColor(fa?.severity)}
          />
          <StatCard
            label="Risk Score"
            value={`${fa?.risk_score || 0}/10`}
            color={scoreColor(fa?.risk_score)}
          />
          <StatCard
            label="Confidence"
            value={`${((fa?.confidence || 0) * 100).toFixed(0)}%`}
            color={confidenceColor(fa?.confidence)}
          />
          <StatCard
            label="Verification"
            value={fa?.verification_status || "—"}
            color={
              fa?.verification_status === "verified"
                ? "text-emerald-400"
                : "text-amber-400"
            }
          />
        </div>
      </div>

      {/* Verification Claims Breakdown */}
      {vr && (
        <div className="cyber-card">
          <h3 className="font-semibold text-base mb-4">
            ✅ Verification Breakdown
          </h3>

          {/* Stats bar */}
          <div className="flex gap-4 mb-4">
            <MiniStat
              label="Supported"
              count={vr.supported_count ?? 0}
              color="bg-emerald-500"
            />
            <MiniStat
              label="Unsupported"
              count={vr.unsupported_count ?? 0}
              color="bg-amber-500"
            />
            <MiniStat
              label="Contradicted"
              count={vr.contradicted_count ?? 0}
              color="bg-red-500"
            />
          </div>

          {/* Evidence quality */}
          {vr.evidence_quality_score !== undefined && (
            <div className="mb-4">
              <p className="text-xs text-[var(--color-cyber-text-dim)] mb-1">
                Evidence Quality Score
              </p>
              <div className="confidence-bar">
                <div
                  className="confidence-bar-fill"
                  style={{
                    width: `${vr.evidence_quality_score * 100}%`,
                    background:
                      vr.evidence_quality_score > 0.7
                        ? "var(--color-cyber-green)"
                        : "var(--color-cyber-orange)",
                  }}
                />
              </div>
              <p className="text-xs text-[var(--color-cyber-text-dim)] mt-0.5">
                {(vr.evidence_quality_score * 100).toFixed(0)}%
              </p>
            </div>
          )}

          {/* Supported */}
          {(vr.supported_claims?.length ?? 0) > 0 && (
            <ClaimSection
              title="Supported Claims"
              icon="✅"
              claims={vr.supported_claims!}
              color="emerald"
            />
          )}

          {/* Unsupported */}
          {(vr.unsupported_claims?.length ?? 0) > 0 && (
            <ClaimSection
              title="Unsupported Claims"
              icon="⚠️"
              claims={vr.unsupported_claims!}
              color="amber"
            />
          )}

          {/* Contradictions */}
          {(vr.contradictions?.length ?? 0) > 0 && (
            <ClaimSection
              title="Contradictions"
              icon="🚫"
              claims={vr.contradictions!}
              color="red"
            />
          )}

          {/* Disagreements */}
          {(vr.disagreements?.length ?? 0) > 0 && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-[var(--color-cyber-text-dim)] uppercase tracking-wider mb-2">
                ⚔️ Agent Disagreements
              </h4>
              <div className="space-y-2">
                {vr.disagreements!.map((d, i) => (
                  <div
                    key={i}
                    className="bg-purple-500/5 border border-purple-500/20 rounded-lg p-3"
                  >
                    <p className="text-sm font-medium text-purple-400 mb-1">
                      {d.topic}
                    </p>
                    <p className="text-xs text-[var(--color-cyber-text-dim)]">
                      <strong>Threat Agent:</strong> {d.threat_agent_position}
                    </p>
                    <p className="text-xs text-[var(--color-cyber-text-dim)]">
                      <strong>Risk Agent:</strong> {d.risk_agent_position}
                    </p>
                    <p className="text-xs text-emerald-400 mt-1">
                      <strong>Evidence:</strong> {d.evidence_assessment}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Corrections */}
          {(vr.corrections_requested?.length ?? 0) > 0 && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-[var(--color-cyber-text-dim)] uppercase tracking-wider mb-2">
                🔧 Corrections Requested
              </h4>
              <ul className="space-y-1">
                {vr.corrections_requested!.map((c, i) => (
                  <li
                    key={i}
                    className="text-sm bg-amber-500/5 border border-amber-500/20 rounded-lg px-3 py-2 text-amber-300"
                  >
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Recommendations */}
      {(fa?.recommendations?.length ?? 0) > 0 && (
        <div className="cyber-card">
          <h3 className="font-semibold text-base mb-3">
            💡 Recommendations
          </h3>
          <ul className="space-y-2">
            {fa!.recommendations.map((r, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm text-[var(--color-cyber-text)]"
              >
                <span className="text-[var(--color-cyber-accent)] mt-0.5 shrink-0">
                  →
                </span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Disclaimer */}
      {fa?.disclaimer && (
        <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
          <p className="text-xs text-amber-400/80 flex items-start gap-2">
            <span className="shrink-0 mt-0.5">⚠️</span>
            {fa.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}

/* ── Sub-components ── */

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="bg-[var(--color-cyber-bg)] rounded-xl p-4 border border-[var(--color-cyber-border)]">
      <p className="text-xs text-[var(--color-cyber-text-dim)] mb-1">{label}</p>
      <p className={`text-xl font-bold ${color}`}>{value}</p>
    </div>
  );
}

function MiniStat({
  label,
  count,
  color,
}: {
  label: string;
  count: number;
  color: string;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className={`w-2.5 h-2.5 rounded-full ${color}`} />
      <span className="text-sm text-[var(--color-cyber-text)]">
        {count} {label}
      </span>
    </div>
  );
}

function ClaimSection({
  title,
  icon,
  claims,
  color,
}: {
  title: string;
  icon: string;
  claims: { claim: string; explanation: string; evidence?: string; missing_evidence?: string }[];
  color: string;
}) {
  return (
    <div className="mt-4">
      <h4 className="text-xs font-semibold text-[var(--color-cyber-text-dim)] uppercase tracking-wider mb-2">
        {icon} {title}
      </h4>
      <div className="space-y-2">
        {claims.map((c, i) => (
          <div
            key={i}
            className={`bg-${color}-500/5 border border-${color}-500/20 rounded-lg p-3`}
          >
            <p className={`text-sm font-medium text-${color}-400`}>
              {c.claim}
            </p>
            <p className="text-xs text-[var(--color-cyber-text-dim)] mt-1">
              {c.explanation}
            </p>
            {c.evidence && (
              <p className="text-xs text-[var(--color-cyber-text-dim)] mt-0.5">
                <span className="font-medium">Evidence:</span> {c.evidence}
              </p>
            )}
            {c.missing_evidence && (
              <p className="text-xs text-amber-400/70 mt-0.5">
                <span className="font-medium">Missing:</span>{" "}
                {c.missing_evidence}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Helpers ── */

function severityColor(s?: string): string {
  switch (s?.toLowerCase()) {
    case "critical":
      return "text-red-400";
    case "high":
      return "text-amber-400";
    case "medium":
      return "text-blue-400";
    case "low":
      return "text-emerald-400";
    default:
      return "text-[var(--color-cyber-text)]";
  }
}

function scoreColor(s?: number): string {
  if (!s) return "text-[var(--color-cyber-text)]";
  if (s >= 8) return "text-red-400";
  if (s >= 6) return "text-amber-400";
  if (s >= 4) return "text-blue-400";
  return "text-emerald-400";
}

function confidenceColor(c?: number): string {
  if (!c) return "text-[var(--color-cyber-text)]";
  if (c >= 0.7) return "text-emerald-400";
  if (c >= 0.4) return "text-amber-400";
  return "text-red-400";
}
