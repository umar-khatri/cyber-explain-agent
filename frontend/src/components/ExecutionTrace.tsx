"use client";

import type { TraceStep } from "@/types";

interface Props {
  trace: TraceStep[];
}

const agentColors: Record<string, string> = {
  "Threat Agent": "border-cyan-500 bg-cyan-500/10",
  "Risk Agent": "border-blue-500 bg-blue-500/10",
  "Verification Agent": "border-purple-500 bg-purple-500/10",
  "Final Assessment": "border-emerald-500 bg-emerald-500/10",
};

const agentDots: Record<string, string> = {
  "Threat Agent": "bg-cyan-500",
  "Risk Agent": "bg-blue-500",
  "Verification Agent": "bg-purple-500",
  "Final Assessment": "bg-emerald-500",
};

export default function ExecutionTrace({ trace }: Props) {
  if (!trace || trace.length === 0) return null;

  const sorted = [...trace].sort((a, b) => a.step_order - b.step_order);

  return (
    <div className="cyber-card">
      <h3 className="font-semibold text-base mb-1">
        ⏱️ Execution Trace
      </h3>
      <p className="text-xs text-[var(--color-cyber-text-dim)] mb-4">
        Chronological record of each agent&apos;s execution
      </p>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-[var(--color-cyber-border)]" />

        <div className="space-y-4">
          {sorted.map((step, i) => {
            const colorClass =
              agentColors[step.agent_name] ||
              "border-slate-500 bg-slate-500/10";
            const dotClass =
              agentDots[step.agent_name] || "bg-slate-500";

            return (
              <div key={i} className="relative pl-10">
                {/* Timeline dot */}
                <div
                  className={`absolute left-2.5 top-3 w-3 h-3 rounded-full ${dotClass} ring-2 ring-[var(--color-cyber-bg)]`}
                />

                <div
                  className={`rounded-lg border-l-2 ${colorClass} p-3`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm">
                        {step.agent_name}
                      </span>
                      <span className={`badge ${step.stage === "revision" ? "badge-high" : step.stage === "final" ? "badge-verified" : "badge-medium"}`}>
                        {step.stage}
                      </span>
                    </div>
                    <span className="text-xs text-[var(--color-cyber-text-dim)] font-mono">
                      {step.duration_ms.toFixed(0)}ms
                    </span>
                  </div>

                  <p className="text-xs text-[var(--color-cyber-text-dim)] mb-0.5">
                    <span className="font-medium">Input:</span>{" "}
                    {step.input_summary}
                  </p>
                  <p className="text-xs text-[var(--color-cyber-text)]">
                    <span className="font-medium">Output:</span>{" "}
                    {step.output_summary}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
