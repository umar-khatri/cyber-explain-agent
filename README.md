# 🛡️ CyberExplain AI

### Explainability and Transparency in Multi-Agent Cybersecurity Decision-Making

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph%200.2-FF6F00?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20(gpt--oss--120b)-F55036?logo=groq&logoColor=white)](https://groq.com/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16%20Turbopack-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React Flow](https://img.shields.io/badge/Graph-React%20Flow-FF0072?logo=react&logoColor=white)](https://reactflow.dev/)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)

---

## 📌 Overview

**CyberExplain AI** demonstrates how multiple specialized AI agents collaborate, fact-check one another, and explain their decisions to produce reliable, audit-ready cybersecurity risk assessments.

In standard single-prompt LLM implementations, speculative claims (e.g., *"the server is fully compromised and customer data has been exfiltrated"*) are often accepted as ground truth, leading to panic-induced **Critical** ratings. **CyberExplain AI** solves this through **multi-agent adversarial verification**: separating threat discovery from risk assessment, evaluating claims against concrete scenario evidence, and automatically executing revisions when assumptions lack factual backing.

---

## 🚀 Key Features

- **Multi-Agent State Orchestration:** Built with **LangGraph** to model state transitions, conditional loops, and revision steps.
- **Evidence vs. Interpretation Separation:** Every threat, indicator, and conclusion is strictly classified as either *Direct Evidence* or *Model Interpretation*.
- **Adversarial Verification Agent:** Evaluates each claim across three statuses:
  - 🟢 **Supported:** Backed by explicit scenario telemetry.
  - 🟡 **Unsupported:** Lacks forensic backing or observational proof.
  - 🔴 **Contradicted:** Conflicts with established constraints (e.g., claiming confirmed compromise when no forensics have occurred).
- **Two-Stage Assessment Comparison:** Real-time before-and-after view showing how initial ratings (e.g. Critical 9.0/10) are recalibrated (e.g. High 7.6/10) after verification.
- **Interactive Graph Visualization:** Interactive node-graph built with **React Flow** showing data flow, execution stage, confidence metrics, and node inspection.
- **Granular Execution Tracing:** Step-by-step latency, input/output summaries, and data passed between agents.
- **Enterprise Persistence:** Storage of assessment runs, execution traces, and decision graphs in **Supabase PostgreSQL**.
- **Complete Documentation & PDF Report:** Bundled 60-page PDF report with complete system architecture and source code listings.

---

## 🏛️ System Architecture

```
                    ┌────────────────────────┐
                    │ Raw Incident Scenario  │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │      Threat Agent      │  Stage 1: Identifies CVEs & IOCs
                    └───────────┬────────────┘
                                │ Threat Analysis
                                ▼
                    ┌────────────────────────┐
                    │       Risk Agent       │  Stage 1: Initial Severity Score
                    └───────────┬────────────┘
                                │ Risk Assessment
                                ▼
                    ┌────────────────────────┐
                    │   Verification Agent   │  Scrutinizes Evidence vs Claims
                    └───────────┬────────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │ Issues Found?             │
                  ▼ (Yes)                     ▼ (No)
     ┌────────────────────────┐               │
     │  Revision Node Loop    │               │
     │ (Threat + Risk Agents) │               │
     └────────────┬───────────┘               │
                  │ Revised Analysis          │
                  └─────────────┬─────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │ Final Synthesis Node   │  Generates Delta & Explainability Report
                    └───────────┬────────────┘
                                │
                                ▼
                  ┌────────────────────────────┐
                  │   Supabase DB + Frontend   │
                  └────────────────────────────┘
```

---

## 🤖 The Three Agents

| Agent | Model Role | System Responsibility |
|---|---|---|
| **Threat Agent** | Cybersecurity Threat Analyst | Parses scenario logs to identify CVEs, network IOCs, and access anomalies. Explicitly separates scenario evidence quotes from model extrapolations. |
| **Risk Agent** | Risk & Impact Assessor | Evaluates operational severity, business impact, and recommendations. Initially factors in all reported observations (provisional Stage 1 score). |
| **Verification Agent** | Fact-Checker & Auditor | Cross-examines all claims against original scenario telemetry. Flags hallucinations, requests specific revisions, and triggers graph routing. |

---

## 🔬 Benchmark Case Study

The system includes a preloaded benchmark scenario designed to demonstrate explainability:

> *"Our company's web application server (running Apache 2.4.49) was accessed from an unusual IP address (203.0.113.42) outside of business hours (3:00 AM local time). The server logs show multiple requests to /cgi-bin/ directories. Additionally, our internal DNS server has been resolving queries for known malicious domains (e.g., malware-c2.evil.example, data-exfil.bad.example). A junior analyst reviewed the logs and claims that the server has already been fully compromised and that attackers have exfiltrated all customer data, based solely on the unusual access pattern. No forensic analysis or memory dump has been performed yet."*

### How the Pipeline Solves This:
1. **Stage 1 (Initial Assessment):** Accepts the analyst claim of customer data exfiltration at face value alongside C2 DNS resolutions $\rightarrow$ Rates severity as **Critical (9.0/10)**.
2. **Verification Agent Critique:**
   - Detects that *"all customer data has been exfiltrated"* is **unsupported** (no outbound byte counts or database queries).
   - Detects that *"server is fully compromised"* **contradicts** the fact that *"no forensic analysis or memory dump has been performed yet"*.
   - Requests immediate revision and downgrading of speculative assumptions.
3. **Stage 2 (Revision):**
   - Reclassifies data exfiltration as an **Unverified Hypothesis** (confidence lowered to 0.18).
   - Recalibrates severity to **High (7.6/10)**, focusing incident response on host containment and memory capture instead of false alarm breach notifications.

---

## 🛠️ Tech Stack

- **Backend:**
  - Python 3.10+ / FastAPI
  - LangGraph 0.2 & LangChain Core
  - Groq API (`openai/gpt-oss-120b`)
  - Supabase Python Client (`supabase-py`)
  - Pydantic v2 Settings & Validation
- **Frontend:**
  - Next.js 16 (Turbopack, App Router)
  - TypeScript
  - Tailwind CSS (Cyberpunk dark aesthetic)
  - React Flow (`@xyflow/react`)
  - Lucide React Icons
- **Database:**
  - Supabase PostgreSQL with JSONB trace columns

---

## 📁 Repository Structure

```
cyber-explain/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application & lifespan
│   │   ├── config.py               # Pydantic BaseSettings & env loading
│   │   ├── models.py               # Request, response, and agent schemas
│   │   ├── database.py             # Supabase client & in-memory cache
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── threat_agent.py     # Threat analysis & prompt templates
│   │   │   ├── risk_agent.py       # Severity estimation & revision
│   │   │   ├── verification_agent.py # Fact-checking & contradiction checker
│   │   │   └── graph.py            # LangGraph StateGraph orchestration
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── assessment.py       # REST API endpoints & sample scenario
│   ├── requirements.txt
│   ├── schema.sql                  # Supabase database schema
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # Main dashboard & pipeline trigger
│   │   │   └── globals.css         # Custom cyberpunk dark styling
│   │   ├── components/
│   │   │   ├── Header.tsx          # App header & branding
│   │   │   ├── ScenarioInput.tsx   # Incident input form & sample loader
│   │   │   ├── AgentGraph.tsx      # React Flow interactive decision graph
│   │   │   ├── AgentNodePanel.tsx  # Selected node deep-dive panel
│   │   │   ├── StageComparison.tsx # Stage 1 vs Stage 2 delta view
│   │   │   ├── ExplainabilityDashboard.tsx # Claims breakdown & evidence
│   │   │   └── ExecutionTrace.tsx  # Chronological latency & data timeline
│   │   ├── lib/
│   │   │   └── api.ts              # Fetch API client
│   │   └── types/
│   │       └── index.ts            # TypeScript definitions & Graph interfaces
│   ├── package.json
│   ├── tailwind.config.ts
│   └── .env.example
├── scripts/
│   └── generate_pdf_report.py      # Automated 60-page PDF report generator
├── CyberExplain_AI_Project_Report.pdf # Full PDF Technical Report
└── README.md
```

---

## ⚡ Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/umar-khatri/cyber-explain-agent.git
cd cyber-explain-agent
```

### 2. Configure Database (Supabase)
1. Create a free project at [supabase.com](https://supabase.com).
2. Navigate to the **SQL Editor** and execute the script in [`backend/schema.sql`](backend/schema.sql):
   ```sql
   CREATE TABLE IF NOT EXISTS assessments (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       scenario TEXT NOT NULL,
       initial_threat_analysis JSONB,
       initial_risk_assessment JSONB,
       verification_result JSONB,
       revised_threat_analysis JSONB,
       revised_risk_assessment JSONB,
       final_assessment JSONB,
       execution_trace JSONB DEFAULT '[]'::jsonb,
       graph_edges JSONB DEFAULT '[]'::jsonb,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );
   CREATE INDEX IF NOT EXISTS idx_assessments_created_at ON assessments (created_at DESC);
   ```
3. Retrieve your **Project URL** and **anon public key** from Project Settings $\rightarrow$ API.

### 3. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `backend/.env` with your API credentials:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL_NAME=openai/gpt-oss-120b
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOi...
HOST=0.0.0.0
PORT=8000
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Frontend Setup
Open a second terminal:
```bash
cd frontend

# Install Node dependencies
npm install

# Configure environment
cp .env.example .env.local
```

Ensure `frontend/.env.local` contains:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the development server:
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check API status and credential detection. |
| `GET` | `/api/sample-scenario` | Get the built-in Apache CVE-2021-41773 benchmark scenario. |
| `POST` | `/api/assess` | Submit a cybersecurity scenario to run the multi-agent pipeline. |
| `GET` | `/api/assessments` | Retrieve the 50 most recent assessments. |
| `GET` | `/api/assessments/{id}` | Retrieve full assessment results and complete execution traces by ID. |

---

## 📄 Comprehensive PDF Report

The repository includes a 60-page PDF report:
- **Location:** [`CyberExplain_AI_Project_Report.pdf`](CyberExplain_AI_Project_Report.pdf)
- To regenerate the report at any time:
  ```bash
  python3 scripts/generate_pdf_report.py
  ```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 👤 Author

**Umar Khatri**  
GitHub: [@umar-khatri](https://github.com/umar-khatri)
