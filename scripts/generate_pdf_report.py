"""Script to generate a comprehensive, professional PDF report with all code listings
for CyberExplain AI: Explainability and Transparency in Multi-Agent Decision-Making.
"""

import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    Preformatted,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas that performs a two-pass calculation to draw 'Page X of Y' and running header."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Skip cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header
        self.drawString(
            54,
            750,
            "CyberExplain AI — Multi-Agent Explainability & Decision-Making Report",
        )
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)

        # Running Footer
        self.line(54, 45, 558, 45)
        self.drawString(
            54,
            33,
            "CONFIDENTIAL & PROPRIETARY — SYSTEM SPECIFICATION & ARCHITECTURE REPORT",
        )
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 33, page_text)
        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#0f172a")  # Dark slate
    accent_color = colors.HexColor("#0284c7")   # Deep cyan
    text_color = colors.HexColor("#1e293b")     # Slate 800

    styles.add(
        ParagraphStyle(
            "CoverTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            textColor=primary_color,
            alignment=1,  # Center
            spaceAfter=15,
        )
    )

    styles.add(
        ParagraphStyle(
            "CoverSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            textColor=accent_color,
            alignment=1,
            spaceAfter=30,
        )
    )

    styles.add(
        ParagraphStyle(
            "CoverMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#475569"),
            alignment=1,
        )
    )

    styles.add(
        ParagraphStyle(
            "SectionH1",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=primary_color,
            spaceBefore=18,
            spaceAfter=8,
            keepWithNext=True,
        )
    )

    styles.add(
        ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=accent_color,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        )
    )

    styles.add(
        ParagraphStyle(
            "SectionH3",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#334155"),
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        )
    )

    styles.add(
        ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=text_color,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            "BodyBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=13,
            textColor=text_color,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            "BulletText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=text_color,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=3,
        )
    )

    styles.add(
        ParagraphStyle(
            "CodeBlockTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=8,
            spaceAfter=3,
            keepWithNext=True,
        )
    )

    styles.add(
        ParagraphStyle(
            "Callout",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=4,
            spaceAfter=6,
        )
    )

    return styles


def read_file_safe(filepath: str) -> str:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"# Error reading {filepath}: {e}"
    return f"# File not found: {filepath}"


def build_code_flowable(title: str, filepath: str, code: str, styles):
    flowables = []

    header_text = f"<b>File:</b> <font color='#0284c7'>{title}</font> &nbsp;&nbsp; <i>({filepath})</i>"
    flowables.append(Paragraph(header_text, styles["CodeBlockTitle"]))

    lines = code.split("\n")
    # Chunk into 45 lines per table so that ReportLab can paginate smoothly across pages
    chunk_size = 45
    total_lines = len(lines)

    for i in range(0, total_lines, chunk_size):
        chunk_lines = lines[i : i + chunk_size]
        # Prepend line numbers for clarity
        numbered_chunk = []
        for line_idx, line in enumerate(chunk_lines, start=i + 1):
            numbered_chunk.append(f"{line_idx:4d} | {line}")
        chunk_text = "\n".join(numbered_chunk)

        pre = Preformatted(
            chunk_text,
            ParagraphStyle(
                "CodeContent",
                fontName="Courier",
                fontSize=6.0,
                leading=7.5,
                textColor=colors.HexColor("#1e293b"),
            ),
        )

        t = Table([[pre]], colWidths=[492])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        flowables.append(t)
        flowables.append(Spacer(1, 2))

    flowables.append(Spacer(1, 8))
    return flowables



def generate_pdf(output_path: str, project_root: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = get_styles()
    story = []

    # =========================================================================
    # 1. COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 80))
    story.append(Paragraph("CYBEREXPLAIN AI", styles["CoverTitle"]))
    story.append(
        Paragraph(
            "Explainability and Transparency in Multi-Agent Cybersecurity Decision-Making",
            styles["CoverSubtitle"],
        )
    )

    story.append(
        HRFlowable(
            width="60%",
            thickness=2,
            color=colors.HexColor("#0ea5e9"),
            spaceBefore=10,
            spaceAfter=25,
            hAlign="CENTER",
        )
    )

    meta_text = f"""
    <b>Technical Architecture, Implementation, and Full Source Code Report</b><br/><br/>
    <b>Author / Engineer:</b> Umar Khatri<br/>
    <b>GitHub Repository:</b> <font color='#0284c7'><u>https://github.com/umar-khatri/cyber-explain-agent</u></font><br/>
    <b>Generated Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
    <b>Status:</b> Production Ready & Tested<br/>
    <b>Backend:</b> Python 3.13, FastAPI, LangGraph, Groq (<code>openai/gpt-oss-120b</code>)<br/>
    <b>Database:</b> Supabase PostgreSQL<br/>
    <b>Frontend:</b> Next.js 16 (App Router), TypeScript, Tailwind CSS, React Flow<br/>
    """
    story.append(Paragraph(meta_text, styles["CoverMeta"]))

    story.append(Spacer(1, 80))

    exec_summary_box = [
        [
            Paragraph(
                "<b>Executive Summary:</b><br/>"
                "CyberExplain AI demonstrates how collaborative multi-agent architectures enhance accuracy, "
                "eliminate ungrounded hallucination, and enforce explainability in high-stakes cybersecurity incident response. "
                "By orchestrating specialized agents (Threat, Risk, and Verification) via LangGraph, the system identifies unsupported "
                "claims, detects contradictions, and dynamically revises assessments before final security recommendations are synthesized.",
                styles["Callout"],
            )
        ]
    ]
    t_box = Table(exec_summary_box, colWidths=[504])
    t_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdfa")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#0d9488")),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(t_box)

    story.append(PageBreak())

    # =========================================================================
    # 2. TABLE OF CONTENTS & OVERVIEW
    # =========================================================================
    story.append(Paragraph("1. System Overview & Problem Statement", styles["SectionH1"]))
    story.append(
        Paragraph(
            "Modern Security Operations Centers (SOCs) are inundated with alerts and speculative analyst summaries. "
            "Conventional large language model (LLM) implementations suffer from confirmation bias and hallucinated certainty: "
            "when presented with an incident containing panic-induced assertions (e.g., 'the server is fully compromised and all customer data is exfiltrated'), "
            "a single-pass model frequently accepts speculative claims as ground truth, elevating severity to Critical and prompting costly, unnecessary incident escalations.",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            "<b>CyberExplain AI resolves this vulnerability through multi-agent adversarial verification:</b>",
            styles["BodyBold"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Independent Threat Formulation:</b> The Threat Agent catalogues observables (e.g., Apache 2.4.49, /cgi-bin/ requests, C2 DNS queries) "
            "while tagging evidence-based indicators versus speculative interpretations.",
            styles["BulletText"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Severity Modeling:</b> The Risk Agent evaluates exploitability, impact, and provisional severity (initially Critical due to alleged data loss).",
            styles["BulletText"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Adversarial Verification:</b> The Verification Agent cross-references every claim directly against the raw incident telemetry, "
            "flagging unsupported assertions, contradictions, and data gaps.",
            styles["BulletText"],
        )
    )
    story.append(
        Paragraph(
            "• <b>Conditional Revision:</b> LangGraph routes the state back through Threat and Risk agents to correct claims, downgrade unverified severities, "
            "and produce an evidence-backed Final Assessment.",
            styles["BulletText"],
        )
    )

    story.append(Spacer(1, 10))

    # Architecture Table
    story.append(Paragraph("2. System Architecture & Workflow", styles["SectionH1"]))

    arch_data = [
        ["Agent / Component", "Role & Responsibility", "Input Source", "Output Artifact"],
        [
            "Threat Agent (Stage 1)",
            "Extracts CVEs, malicious IPs, DNS domains, and access patterns.",
            "Raw Scenario Text",
            "Threats list, evidence quotes, model interpretations.",
        ],
        [
            "Risk Agent (Stage 1)",
            "Calculates initial risk score (0-10) and severity rating.",
            "Threat Analysis + Scenario",
            "Severity, risk score, preliminary recommendations.",
        ],
        [
            "Verification Agent",
            "Critiques claims, isolates contradictions, flags unsupported leaps.",
            "Scenario + Threat + Risk",
            "Supported/Unsupported claims, requested corrections.",
        ],
        [
            "Revision Loop (Stage 2)",
            "Revises threats, lowers confidence, recalibrates severity.",
            "Verification Feedback",
            "Revised threats and downgraded realistic risk score.",
        ],
        [
            "Final Synthesis Node",
            "Generates executive report and Before/After stage metrics.",
            "All Agent State",
            "Consolidated assessment with transparent explainability.",
        ],
        [
            "Supabase PostgreSQL",
            "Persists assessment runs, node telemetry, and graph edges.",
            "FastAPI Assessment Router",
            "Persistent UUIDs, timestamps, and queryable audit trails.",
        ],
    ]
    t_arch = Table(arch_data, colWidths=[110, 150, 110, 134])
    t_arch.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
            ]
        )
    )
    story.append(t_arch)

    story.append(Spacer(1, 12))

    story.append(Paragraph("3. Multi-Agent Decision State Graph (LangGraph)", styles["SectionH1"]))
    story.append(
        Paragraph(
            "The multi-agent system is compiled into a cyclic StateGraph using LangGraph. "
            "Unlike linear chains, LangGraph allows conditional branches where the graph autonomously decides whether "
            "to route to <code>revision</code> or straight to <code>finalize_assessment</code> based on the Verification Agent's <code>overall_status</code>.",
            styles["Body"],
        )
    )

    langgraph_ascii = """
                             [ Start: Scenario Input ]
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │    Threat Agent     │ (Identifies CVE-2021-41773 & C2 DNS)
                             └──────────┬──────────┘
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │     Risk Agent      │ (Assesses Initial Severity: Critical)
                             └──────────┬──────────┘
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │ Verification Agent  │ (Scrutinizes Evidence vs Claims)
                             └──────────┬──────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         ▼ (needs_revision)            ▼ (passed)
              ┌─────────────────────┐                  │
              │    Revision Step    │                  │
              │  (Threat + Risk)    │                  │
              └──────────┬──────────┘                  │
                         │                             │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │ Finalize Assessment │ (Computes Stage 1 vs 2 Delta)
                             └──────────┬──────────┘
                                        │
                                        ▼
                                     [ End ]
    """
    story.append(
        Preformatted(
            langgraph_ascii,
            ParagraphStyle(
                "AsciiGraph",
                fontName="Courier",
                fontSize=7.5,
                leading=9.5,
                textColor=colors.HexColor("#0369a1"),
            ),
        )
    )

    story.append(PageBreak())

    # =========================================================================
    # 3. EXPLAINABILITY MECHANISM & CASE STUDY
    # =========================================================================
    story.append(Paragraph("4. Deep Dive: Explainability & The Benchmark Scenario", styles["SectionH1"]))
    story.append(
        Paragraph(
            "<b>The Benchmark Cybersecurity Scenario:</b><br/>"
            "<i>\"Our company's web application server (running Apache 2.4.49) was accessed from an unusual IP address (203.0.113.42) "
            "outside of business hours (3:00 AM local time). The server logs show multiple requests to /cgi-bin/ directories. "
            "Additionally, our internal DNS server has been resolving queries for known malicious domains (e.g., malware-c2.evil.example, data-exfil.bad.example). "
            "A junior analyst reviewed the logs and claims that the server has already been fully compromised and that attackers have exfiltrated all customer data, "
            "based solely on the unusual access pattern. No forensic analysis or memory dump has been performed yet.\"</i>",
            styles["Body"],
        )
    )

    story.append(
        Paragraph(
            "<b>How Explainability Solves the Assessment Problem:</b>",
            styles["BodyBold"],
        )
    )

    case_data = [
        ["Phase", "Severity", "Risk Score", "Confidence", "Key Finding & Evidence Grounding"],
        [
            "Stage 1 (Initial)",
            "Critical",
            "9.0 / 10",
            "0.65",
            "Analyst claim of mass customer data exfiltration is taken at face value. "
            "Alarming panic state triggered despite lack of evidence.",
        ],
        [
            "Verification",
            "Needs Revision",
            "—",
            "—",
            "Identifies that claim 'Server fully compromised and all data exfiltrated' has ZERO supporting evidence. "
            "Contradicts explicit statement that no memory dump or forensics were executed.",
        ],
        [
            "Stage 2 (Revised)",
            "High",
            "7.6 / 10",
            "0.88",
            "Exfiltration downgraded to 'Unverified Hypothesis' with 0.18 confidence. "
            "Active Apache 2.4.49 exploit probes and C2 DNS are confirmed, focusing response on host isolation and memory acquisition.",
        ],
    ]
    t_case = Table(case_data, colWidths=[80, 70, 60, 60, 234])
    t_case.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    story.append(t_case)

    story.append(Spacer(1, 14))

    # =========================================================================
    # 4. DATABASE & API SPECIFICATION
    # =========================================================================
    story.append(Paragraph("5. Database Schema & REST API Specifications", styles["SectionH1"]))
    story.append(
        Paragraph(
            "<b>PostgreSQL Persistence (Supabase):</b> Assessments and complete execution traces are stored in the <code>assessments</code> table. "
            "JSONB columns allow rapid serialization of dynamic agent outputs, graph edges, and per-step timing.",
            styles["Body"],
        )
    )

    api_data = [
        ["Method", "Endpoint", "Description", "Payload / Return"],
        ["GET", "/health", "System health & credentials status", "<code>{'status': 'ok', 'groq_configured': bool, ...}</code>"],
        ["GET", "/api/sample-scenario", "Retrieves benchmark cyber incident", "<code>{'scenario': string}</code>"],
        ["POST", "/api/assess", "Executes full multi-agent LangGraph pipeline", "Body: <code>ScenarioRequest</code> → <code>AssessmentResponse</code>"],
        ["GET", "/api/assessments", "Lists recent 50 assessments", "<code>{'assessments': list[AssessmentListItem]}</code>"],
        ["GET", "/api/assessments/{id}", "Fetches detailed assessment & full trace", "Returns complete <code>AssessmentResponse</code>"],
    ]
    t_api = Table(api_data, colWidths=[55, 145, 154, 150])
    t_api.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    story.append(t_api)

    story.append(PageBreak())

    # =========================================================================
    # 5. COMPLETE CODE BASE LISTINGS
    # =========================================================================
    story.append(Paragraph("6. Complete Source Code Listings", styles["SectionH1"]))
    story.append(
        Paragraph(
            "This section contains the full, verified source code files implementing the backend agents, orchestration graph, "
            "data models, database integrations, API endpoints, schema definitions, and frontend components.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 8))

    files_to_include = [
        # Backend Core
        ("Database Schema (Supabase SQL)", "backend/schema.sql"),
        ("Configuration & LLM Settings", "backend/app/config.py"),
        ("Pydantic Data Models & Types", "backend/app/models.py"),
        ("Supabase Client & In-Memory Store", "backend/app/database.py"),
        ("FastAPI Application Entry Point", "backend/app/main.py"),
        ("Assessment & Pipeline Routes", "backend/app/routes/assessment.py"),
        # Agents
        ("Threat Agent Implementation", "backend/app/agents/threat_agent.py"),
        ("Risk Agent Implementation", "backend/app/agents/risk_agent.py"),
        ("Verification Agent Implementation", "backend/app/agents/verification_agent.py"),
        ("LangGraph Pipeline Orchestration", "backend/app/agents/graph.py"),
        # Frontend Core
        ("TypeScript Types & Graph Node Definitions", "frontend/src/types/index.ts"),
        ("API Integration Client", "frontend/src/lib/api.ts"),
        ("Main Page Application Container", "frontend/src/app/page.tsx"),
        ("Interactive Decision Graph (React Flow)", "frontend/src/components/AgentGraph.tsx"),
        ("Explainability Claims Dashboard", "frontend/src/components/ExplainabilityDashboard.tsx"),
        ("Stage 1 vs Stage 2 Comparison", "frontend/src/components/StageComparison.tsx"),
    ]

    for title, rel_path in files_to_include:
        full_path = os.path.join(project_root, rel_path)
        code_content = read_file_safe(full_path)
        story.extend(build_code_flowable(title, rel_path, code_content, styles))

    # =========================================================================
    # 6. SETUP & EXECUTION MANUAL
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("7. Setup, Deployment & Verification Manual", styles["SectionH1"]))

    manual_text = """
    <b>1. GitHub Repository & Prerequisites:</b><br/>
    • GitHub Repository: <code>https://github.com/umar-khatri/cyber-explain-agent.git</code><br/>
    • Python ≥ 3.10 (Tested on Python 3.13 macOS ARM64)<br/>
    • Node.js ≥ 18 (Tested with Next.js 16.4 Turbopack)<br/>
    • Groq API Key (using free tier <code>openai/gpt-oss-120b</code>)<br/>
    • Supabase Account (with executed <code>backend/schema.sql</code>)<br/><br/>

    <b>2. Backend Setup:</b><br/>
    <pre>
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    # Populate GROQ_API_KEY, SUPABASE_URL, and SUPABASE_KEY in .env
    uvicorn app.main:app --reload --port 8000
    </pre>
    API documentation available at: <code>http://localhost:8000/docs</code><br/><br/>

    <b>3. Frontend Setup:</b><br/>
    <pre>
    cd frontend
    npm install
    # Ensure .env.local has NEXT_PUBLIC_API_URL=http://localhost:8000
    npm run dev
    </pre>
    Web application available at: <code>http://localhost:3000</code><br/><br/>

    <b>4. End-to-End Test Execution:</b><br/>
    The backend test suite validates all endpoints and simulates the multi-agent decision cycle:
    <pre>
    python3 -m py_compile backend/app/*.py backend/app/agents/*.py backend/app/routes/*.py
    cd frontend && npm run build
    </pre>
    """
    story.append(Paragraph(manual_text, styles["Body"]))

    # =========================================================================
    # 7. CONCLUSION
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("8. Conclusion & Future Directions", styles["SectionH1"]))
    story.append(
        Paragraph(
            "CyberExplain AI successfully demonstrates that multi-agent architectures provide the essential checks and balances "
            "required for enterprise AI adoption in cybersecurity. By disaggregating threat detection from severity rating and introducing "
            "an explicit verification agent that challenges ungrounded assertions, organizations can prevent costly hallucinated incident panics "
            "while maintaining complete auditability through transparent execution traces.",
            styles["Body"],
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report PDF successfully generated at: {output_path}")


if __name__ == "__main__":
    project_dir = "/Users/umarkhatri/Projects/cyber-explain"
    out_file = os.path.join(project_dir, "CyberExplain_AI_Project_Report.pdf")
    generate_pdf(out_file, project_dir)
