-- CyberExplain AI: Supabase Schema
-- Run this in the Supabase SQL Editor to create the required tables.

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

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_assessments_created_at ON assessments (created_at DESC);

-- Enable Row Level Security (optional, disable for dev)
-- ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow all" ON assessments FOR ALL USING (true);
