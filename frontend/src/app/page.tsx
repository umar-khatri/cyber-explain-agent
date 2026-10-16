"use client";

import { useState, useCallback, useEffect } from "react";
import Header from "@/components/Header";
import ScenarioInput from "@/components/ScenarioInput";
import AgentGraph from "@/components/AgentGraph";
import AgentNodePanel from "@/components/AgentNodePanel";
import StageComparison from "@/components/StageComparison";
import ExecutionTrace from "@/components/ExecutionTrace";
import ExplainabilityDashboard from "@/components/ExplainabilityDashboard";
import { fetchSampleScenario, runAssessment } from "@/lib/api";
import type { AssessmentResult } from "@/types";

const FALLBACK_SAMPLE = `Our company's web application server (running Apache 2.4.49) was accessed from an unusual IP address (203.0.113.42) outside of business hours (3:00 AM local time). The server logs show multiple requests to /cgi-bin/ directories. Additionally, our internal DNS server has been resolving queries for known malicious domains (e.g., malware-c2.evil.example, data-exfil.bad.example). A junior analyst reviewed the logs and claims that the server has already been fully compromised and that attackers have exfiltrated all customer data, based solely on the unusual access pattern. No forensic analysis or memory dump has been performed yet.`;

export default function Home() {
  const [sampleScenario, setSampleScenario] = useState(FALLBACK_SAMPLE);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assessment, setAssessment] = useState<AssessmentResult | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"graph" | "dashboard" | "trace">(
    "graph"
  );

  // Fetch sample scenario from backend on mount
  useEffect(() => {
    fetchSampleScenario()
      .then(setSampleScenario)
      .catch(() => {
        /* fallback already set */
      });
  }, []);

  const handleSubmit = useCallback(async (scenario: string) => {
    setIsLoading(true);
    setError(null);
    setAssessment(null);
    setSelectedNode(null);

    try {
      const result = await runAssessment(scenario);
      setAssessment(result);
      setActiveTab("graph");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleNodeSelect = useCallback((nodeId: string) => {
    setSelectedNode((prev) => (prev === nodeId ? null : nodeId));
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto px-6 py-8 w-full">
        {/* Scenario Input */}
        <section className="mb-8">
          <ScenarioInput
            onSubmit={handleSubmit}
            sampleScenario={sampleScenario}
            isLoading={isLoading}
          />
        </section>

        {/* Loading state */}
        {isLoading && (
          <div className="cyber-card flex flex-col items-center justify-center py-16 glow-cyan">
            <div className="spinner mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              Multi-Agent Analysis in Progress
            </h3>
            <p className="text-sm text-[var(--color-cyber-text-dim)] max-w-md text-center">
              Threat Agent → Risk Agent → Verification Agent → Revision (if needed) → Final Assessment
            </p>
            <div className="flex gap-3 mt-4">
              {["Threat", "Risk", "Verify", "Revise", "Final"].map((s, i) => (
                <span
                  key={s}
                  className="badge badge-medium animate-pulse"
                  style={{ animationDelay: `${i * 0.3}s` }}
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="cyber-card border-red-500/30 glow-red mb-8">
            <div className="flex items-start gap-3">
              <span className="text-red-400 text-xl">⚠️</span>
              <div>
                <h3 className="font-semibold text-red-400">
                  Assessment Failed
                </h3>
                <p className="text-sm text-[var(--color-cyber-text-dim)] mt-1">
                  {error}
                </p>
                <p className="text-xs text-[var(--color-cyber-text-dim)] mt-2">
                  Make sure the backend is running on{" "}
                  <code className="text-[var(--color-cyber-accent)]">
                    http://localhost:8000
                  </code>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {assessment && !isLoading && (
          <>
            {/* Tab navigation */}
            <div className="flex gap-1 mb-6 bg-[var(--color-cyber-surface)] rounded-xl p-1 border border-[var(--color-cyber-border)] w-fit">
              {(
                [
                  { key: "graph", label: "🔗 Decision Graph", },
                  { key: "dashboard", label: "📊 Dashboard" },
                  { key: "trace", label: "⏱️ Trace" },
                ] as const
              ).map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    activeTab === tab.key
                      ? "bg-[var(--color-cyber-accent)]/15 text-[var(--color-cyber-accent)] border border-[var(--color-cyber-accent)]/30"
                      : "text-[var(--color-cyber-text-dim)] hover:text-[var(--color-cyber-text)]"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Graph tab */}
            {activeTab === "graph" && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                <div className="lg:col-span-2">
                  <AgentGraph
                    assessment={assessment}
                    onNodeSelect={handleNodeSelect}
                  />
                </div>
                <div>
                  {selectedNode ? (
                    <AgentNodePanel
                      assessment={assessment}
                      selectedNodeId={selectedNode}
                      onClose={() => setSelectedNode(null)}
                    />
                  ) : (
                    <div className="cyber-card flex flex-col items-center justify-center py-16 text-center">
                      <p className="text-4xl mb-3">👆</p>
                      <p className="text-sm text-[var(--color-cyber-text-dim)]">
                        Click any node in the graph to inspect its details
                      </p>
                      <p className="text-xs text-[var(--color-cyber-text-dim)] mt-2">
                        View input, conclusion, evidence, confidence, and model
                        interpretations
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Dashboard tab */}
            {activeTab === "dashboard" && (
              <div className="mb-8">
                <ExplainabilityDashboard assessment={assessment} />
              </div>
            )}

            {/* Trace tab */}
            {activeTab === "trace" && (
              <div className="mb-8">
                <ExecutionTrace trace={assessment.execution_trace} />
              </div>
            )}

            {/* Stage comparison always visible below tabs */}
            <section className="mb-8">
              <StageComparison assessment={assessment} />
            </section>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--color-cyber-border)] py-4">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between text-xs text-[var(--color-cyber-text-dim)]">
          <p>CyberExplain AI — College Mini-Project</p>
          <p>
            Powered by LangGraph + Groq + Next.js
          </p>
        </div>
      </footer>
    </div>
  );
}
