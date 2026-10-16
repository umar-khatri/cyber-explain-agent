"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  BackgroundVariant,
  type Node,
  type Edge,
  type NodeTypes,
  Handle,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type {
  AssessmentResult,
  AgentNodeData,
  GraphEdge as GEdge,
} from "@/types";

/* ── Custom node component ── */

interface CustomNodeProps {
  data: AgentNodeData & { onSelect: (id: string) => void };
}

const stageColors: Record<string, { bg: string; border: string; glow: string }> = {
  input: {
    bg: "from-slate-600/20 to-slate-700/20",
    border: "border-slate-500/40",
    glow: "",
  },
  initial: {
    bg: "from-cyan-600/20 to-blue-700/20",
    border: "border-cyan-500/40",
    glow: "glow-cyan",
  },
  revision: {
    bg: "from-amber-600/20 to-orange-700/20",
    border: "border-amber-500/40",
    glow: "glow-orange",
  },
  final: {
    bg: "from-emerald-600/20 to-green-700/20",
    border: "border-emerald-500/40",
    glow: "glow-green",
  },
};

const stageIcons: Record<string, string> = {
  input: "📋",
  initial: "🔍",
  revision: "🔄",
  final: "✅",
};

function AgentNode({ data }: CustomNodeProps) {
  const colors = stageColors[data.stage] || stageColors.initial;
  const icon = stageIcons[data.stage] || "🔍";

  return (
    <div
      onClick={() => data.onSelect(data.id)}
      className={`
        cursor-pointer rounded-xl border ${colors.border} ${data.active ? colors.glow : ""}
        bg-gradient-to-br ${colors.bg} backdrop-blur-sm
        px-5 py-3.5 min-w-[180px] transition-all duration-300
        hover:scale-[1.03] hover:shadow-lg
        ${data.active ? "ring-1 ring-cyan-400/30" : ""}
      `}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-[var(--color-cyber-accent)] !border-[var(--color-cyber-bg)] !w-2.5 !h-2.5"
      />

      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-base">{icon}</span>
        <span className="font-semibold text-sm text-[var(--color-cyber-text)]">
          {data.label}
        </span>
      </div>

      {data.status && (
        <span className={`badge badge-${data.status.toLowerCase().replace(/ /g, "_")}`}>
          {data.status}
        </span>
      )}

      {data.confidence !== undefined && data.confidence > 0 && (
        <div className="mt-2">
          <div className="confidence-bar">
            <div
              className="confidence-bar-fill"
              style={{
                width: `${data.confidence * 100}%`,
                background:
                  data.confidence > 0.7
                    ? "var(--color-cyber-green)"
                    : data.confidence > 0.4
                    ? "var(--color-cyber-orange)"
                    : "var(--color-cyber-red)",
              }}
            />
          </div>
          <p className="text-[10px] text-[var(--color-cyber-text-dim)] mt-0.5">
            Confidence: {(data.confidence * 100).toFixed(0)}%
          </p>
        </div>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-[var(--color-cyber-accent)] !border-[var(--color-cyber-bg)] !w-2.5 !h-2.5"
      />
    </div>
  );
}

const nodeTypes: NodeTypes = { agentNode: AgentNode };

/* ── Build nodes & edges from assessment data ── */

interface Props {
  assessment: AssessmentResult;
  onNodeSelect: (nodeId: string) => void;
}

export default function AgentGraph({ assessment, onNodeSelect }: Props) {
  const onSelect = useCallback(
    (id: string) => onNodeSelect(id),
    [onNodeSelect]
  );

  const revisionHappened =
    assessment.final_assessment?.before_after?.revision_performed ?? false;

  const nodes: Node[] = useMemo(() => {
    const base: Node[] = [
      {
        id: "scenario_input",
        type: "agentNode",
        position: { x: 300, y: 0 },
        data: {
          id: "scenario_input",
          label: "Scenario Input",
          stage: "input",
          active: true,
          onSelect,
        } as AgentNodeData & { onSelect: (id: string) => void },
      },
      {
        id: "threat_agent",
        type: "agentNode",
        position: { x: 150, y: 120 },
        data: {
          id: "threat_agent",
          label: "Threat Agent",
          stage: "initial",
          confidence:
            assessment.initial_threat_analysis?.overall_confidence ?? 0,
          status:
            (assessment.initial_threat_analysis?.threats?.length ?? 0) > 0
              ? `${assessment.initial_threat_analysis?.threats?.length} threats`
              : undefined,
          active: true,
          onSelect,
        } as AgentNodeData & { onSelect: (id: string) => void },
      },
      {
        id: "risk_agent",
        type: "agentNode",
        position: { x: 450, y: 120 },
        data: {
          id: "risk_agent",
          label: "Risk Agent",
          stage: "initial",
          confidence: assessment.initial_risk_assessment?.confidence ?? 0,
          status: assessment.initial_risk_assessment?.severity,
          active: true,
          onSelect,
        } as AgentNodeData & { onSelect: (id: string) => void },
      },
      {
        id: "verification_agent",
        type: "agentNode",
        position: { x: 300, y: 260 },
        data: {
          id: "verification_agent",
          label: "Verification Agent",
          stage: "initial",
          confidence:
            assessment.verification_result?.evidence_quality_score ?? 0,
          status: assessment.verification_result?.overall_status,
          active: true,
          onSelect,
        } as AgentNodeData & { onSelect: (id: string) => void },
      },
    ];

    if (revisionHappened) {
      base.push(
        {
          id: "threat_agent_revision",
          type: "agentNode",
          position: { x: 100, y: 400 },
          data: {
            id: "threat_agent_revision",
            label: "Threat Agent (Revised)",
            stage: "revision",
            confidence:
              assessment.revised_threat_analysis?.overall_confidence ?? 0,
            active: true,
            onSelect,
          } as AgentNodeData & { onSelect: (id: string) => void },
        },
        {
          id: "risk_agent_revision",
          type: "agentNode",
          position: { x: 500, y: 400 },
          data: {
            id: "risk_agent_revision",
            label: "Risk Agent (Revised)",
            stage: "revision",
            confidence:
              assessment.revised_risk_assessment?.confidence ?? 0,
            status: assessment.revised_risk_assessment?.severity,
            active: true,
            onSelect,
          } as AgentNodeData & { onSelect: (id: string) => void },
        }
      );
    }

    base.push({
      id: "final_assessment",
      type: "agentNode",
      position: { x: 300, y: revisionHappened ? 540 : 400 },
      data: {
        id: "final_assessment",
        label: "Final Assessment",
        stage: "final",
        confidence: assessment.final_assessment?.confidence ?? 0,
        status: assessment.final_assessment?.severity,
        active: true,
        onSelect,
      } as AgentNodeData & { onSelect: (id: string) => void },
    });

    return base;
  }, [assessment, revisionHappened, onSelect]);

  const edges: Edge[] = useMemo(() => {
    const base: Edge[] = [
      {
        id: "e-input-threat",
        source: "scenario_input",
        target: "threat_agent",
        animated: true,
        label: "scenario",
        style: { stroke: "var(--color-cyber-accent)" },
        labelStyle: { fill: "var(--color-cyber-text-dim)", fontSize: 10 },
      },
      {
        id: "e-input-risk",
        source: "scenario_input",
        target: "risk_agent",
        animated: true,
        label: "scenario",
        style: { stroke: "var(--color-cyber-accent)" },
        labelStyle: { fill: "var(--color-cyber-text-dim)", fontSize: 10 },
      },
      {
        id: "e-threat-verify",
        source: "threat_agent",
        target: "verification_agent",
        animated: true,
        label: "threats",
        style: { stroke: "var(--color-cyber-blue)" },
        labelStyle: { fill: "var(--color-cyber-text-dim)", fontSize: 10 },
      },
      {
        id: "e-risk-verify",
        source: "risk_agent",
        target: "verification_agent",
        animated: true,
        label: "risk assessment",
        style: { stroke: "var(--color-cyber-blue)" },
        labelStyle: { fill: "var(--color-cyber-text-dim)", fontSize: 10 },
      },
    ];

    if (revisionHappened) {
      base.push(
        {
          id: "e-verify-threat-rev",
          source: "verification_agent",
          target: "threat_agent_revision",
          animated: true,
          label: "corrections",
          style: { stroke: "var(--color-cyber-orange)" },
          labelStyle: { fill: "var(--color-cyber-text-dim)", fontSize: 10 },
        },
        {
          id: "e-verify-risk-rev",
          source: "verification_agent",
          target: "risk_agent_revision",
          animated: true,
          label: "corrections",
          style: { stroke: "var(--color-cyber-orange)" },
          labelStyle: { fill: "var(--color-cyber-text-dim)", fontSize: 10 },
        },
        {
          id: "e-threat-rev-final",
          source: "threat_agent_revision",
          target: "final_assessment",
          animated: true,
          label: "revised threats",
          style: { stroke: "var(--color-cyber-green)" },
          labelStyle: { fill: "var(--color-cyber-text-dim)", fontSize: 10 },
        },
        {
          id: "e-risk-rev-final",
          source: "risk_agent_revision",
          target: "final_assessment",
          animated: true,
          label: "revised risk",
          style: { stroke: "var(--color-cyber-green)" },
          labelStyle: { fill: "var(--color-cyber-text-dim)", fontSize: 10 },
        }
      );
    } else {
      base.push({
        id: "e-verify-final",
        source: "verification_agent",
        target: "final_assessment",
        animated: true,
        label: "verified",
        style: { stroke: "var(--color-cyber-green)" },
        labelStyle: { fill: "var(--color-cyber-text-dim)", fontSize: 10 },
      });
    }

    return base;
  }, [revisionHappened]);

  return (
    <div className="cyber-card p-0 overflow-hidden" style={{ height: revisionHappened ? 680 : 520 }}>
      <div className="px-5 py-3 border-b border-[var(--color-cyber-border)] flex items-center justify-between">
        <h3 className="font-semibold text-sm">
          🔗 Agent Decision Graph
        </h3>
        <p className="text-xs text-[var(--color-cyber-text-dim)]">
          Click any node to inspect details
        </p>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        proOptions={{ hideAttribution: true }}
        minZoom={0.5}
        maxZoom={1.5}
        nodesDraggable={true}
        nodesConnectable={false}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="var(--color-cyber-border)" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
