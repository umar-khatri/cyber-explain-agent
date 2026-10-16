/* ── API client for the FastAPI backend ── */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchSampleScenario(): Promise<string> {
  const res = await fetch(`${API_BASE}/api/sample-scenario`);
  if (!res.ok) throw new Error("Failed to fetch sample scenario");
  const data = await res.json();
  return data.scenario;
}

export async function runAssessment(scenario: string) {
  const res = await fetch(`${API_BASE}/api/assess`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "Assessment failed");
  }
  return res.json();
}

export async function fetchAssessments() {
  const res = await fetch(`${API_BASE}/api/assessments`);
  if (!res.ok) throw new Error("Failed to fetch assessments");
  const data = await res.json();
  return data.assessments;
}

export async function fetchAssessment(id: string) {
  const res = await fetch(`${API_BASE}/api/assessments/${id}`);
  if (!res.ok) throw new Error("Failed to fetch assessment");
  return res.json();
}
