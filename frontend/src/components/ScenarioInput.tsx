"use client";

import { useState } from "react";

interface Props {
  onSubmit: (scenario: string) => void;
  sampleScenario: string;
  isLoading: boolean;
}

export default function ScenarioInput({
  onSubmit,
  sampleScenario,
  isLoading,
}: Props) {
  const [scenario, setScenario] = useState("");

  const handleLoadSample = () => {
    setScenario(sampleScenario);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (scenario.trim().length >= 10) {
      onSubmit(scenario.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="cyber-card glow-cyan">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-[var(--color-cyber-text)]">
            Cybersecurity Scenario
          </h2>
          <p className="text-sm text-[var(--color-cyber-text-dim)] mt-0.5">
            Describe a scenario for multi-agent analysis
          </p>
        </div>
        <button
          type="button"
          onClick={handleLoadSample}
          className="btn-secondary text-sm"
          disabled={isLoading}
        >
          ⚡ Load Sample
        </button>
      </div>

      <textarea
        value={scenario}
        onChange={(e) => setScenario(e.target.value)}
        placeholder="Enter a cybersecurity scenario to analyse…"
        rows={6}
        disabled={isLoading}
        className="w-full bg-[var(--color-cyber-bg)] border border-[var(--color-cyber-border)] rounded-lg p-4 text-sm text-[var(--color-cyber-text)] placeholder:text-[var(--color-cyber-text-dim)]/50 focus:outline-none focus:border-[var(--color-cyber-accent)] focus:ring-1 focus:ring-[var(--color-cyber-accent)]/30 resize-none transition-colors font-[family-name:var(--font-mono)]"
      />

      <div className="flex items-center justify-between mt-4">
        <p className="text-xs text-[var(--color-cyber-text-dim)]">
          {scenario.length} characters
          {scenario.length > 0 && scenario.length < 10 && (
            <span className="text-[var(--color-cyber-orange)] ml-2">
              — Minimum 10 characters
            </span>
          )}
        </p>
        <button
          type="submit"
          disabled={isLoading || scenario.trim().length < 10}
          className="btn-primary flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <span className="spinner !w-4 !h-4 !border-2" />
              Analysing…
            </>
          ) : (
            <>
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
                />
              </svg>
              Run Assessment
            </>
          )}
        </button>
      </div>
    </form>
  );
}
