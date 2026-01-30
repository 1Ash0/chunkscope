-- ChunkScope Database Schema (PostgreSQL + pgvector)
-- Migration: 001_init_schema.sql
-- Version: 1.0.0

-- ============================================
-- EXTENSIONS
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================
-- ENUMS
-- ============================================
CREATE TYPE document_type AS ENUM ('pdf', 'txt', 'md', 'docx', 'html', 'code');
CREATE TYPE pipeline_status AS ENUM ('draft', 'running', 'completed', 'failed');
CREATE TYPE evaluation_status AS ENUM ('pending', 'running', 'completed', 'failed');
CREATE TYPE chunking_method AS ENUM (
    'fixed_size', 'recursive', 'semantic', 'sentence', 
    'paragraph', 'markdown', 'code', 'table', 'heading', 'agentic'
);

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- PIPELINES TABLE
-- ============================================
-- Stores RAG pipeline configurations with nodes and edges as JSONB
-- JSONB chosen because:
-- 1. Schema varies by node type (10+ types with different configs)
-- 2. Always read/written as complete graph
-- 3. GIN index supports filtering by node type

CREATE TABLE pipelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status pipeline_status DEFAULT 'draft',
    
    -- JSONB for flexible node/edge storage
    -- Example nodes: [{"id": "n1", "type": "chunker", "config": {...}}]
    nodes JSONB DEFAULT '[]',
    
    -- Example edges: [{"source": "n1", "target": "n2"}]
    edges JSONB DEFAULT '[]',
    
    -- Pipeline-level settings
    settings JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- B-tree for user lookup
CREATE INDEX idx_pipelines_user_id ON pipelines(user_id);

-- GIN for querying nodes by type: WHERE nodes @> '[{"type": "chunker"}]'
CREATE INDEX idx_pipelines_nodes ON pipelines USING GIN(nodes);

-- ============================================
-- PIPELINE VERSIONS TABLE
-- ============================================
-- Version history for pipelines (immutable snapshots)

CREATE TABLE pipeline_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    config JSONB NOT NULL, -- Full snapshot: {nodes, edges, settings}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(pipeline_id, version_number)
);

CREATE INDEX idx_pipeline_versions_pipeline_id ON pipeline_versions(pipeline_id);

-- ============================================
-- DOCUMENTS TABLE
-- ============================================
-- Stores uploaded documents with metadata

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_type document_type NOT NULL,
    file_size_bytes BIGINT,
    
    -- JSONB for variable metadata (page_count, author, etc.)
    metadata JSONB DEFAULT '{}',
    
    -- Extracted text (nullable, populated after processing)
    extracted_text TEXT,
    
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_file_type ON documents(file_type);

-- ============================================
-- CHUNKS TABLE
-- ============================================
-- Stores text chunks with vector embeddings
-- This is the core table for RAG retrieval

CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    pipeline_version_id UUID REFERENCES pipeline_versions(id) ON DELETE SET NULL,
    
    -- Chunk content
    text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    
    -- Vector embedding (1536 for OpenAI, configurable)
    embedding vector(1536),
    
    -- Chunking configuration used
    chunking_method chunking_method,
    chunk_size INTEGER,
    chunk_overlap INTEGER,
    
    -- JSONB for variable metadata:
    -- PDF: {page: 1, bbox: {x, y, w, h}}
    -- Code: {line_start: 10, line_end: 25, function: "foo"}
    metadata JSONB DEFAULT '{}',
    
    -- Token count for cost estimation
    token_count INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- B-tree for document pagination
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chunks_document_idx ON chunks(document_id, chunk_index);

-- HNSW index for cosine similarity search
-- m=16: connections per node (higher = more accurate, more memory)
-- ef_construction=64: build-time search depth
CREATE INDEX idx_chunks_embedding ON chunks 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- GIN for metadata queries: WHERE metadata @> '{"page": 5}'
CREATE INDEX idx_chunks_metadata ON chunks USING GIN(metadata);

-- ============================================
-- TEST DATASETS TABLE
-- ============================================
-- Stores golden Q&A pairs for evaluation

CREATE TABLE test_datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Array of Q&A pairs: [{"query": "...", "expected_answer": "...", "expected_chunks": [...]}]
    questions JSONB DEFAULT '[]',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_test_datasets_user_id ON test_datasets(user_id);

-- ============================================
-- EVALUATIONS TABLE
-- ============================================
-- Stores A/B test sessions

CREATE TABLE evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    
    -- Pipeline being tested
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    pipeline_version_id UUID REFERENCES pipeline_versions(id),
    
    -- Test dataset used
    test_dataset_id UUID REFERENCES test_datasets(id) ON DELETE SET NULL,
    
    -- For A/B testing: compare against this pipeline
    comparison_pipeline_id UUID REFERENCES pipelines(id) ON DELETE SET NULL,
    
    status evaluation_status DEFAULT 'pending',
    
    -- Aggregate scores: {avg_context_relevance: 0.85, avg_faithfulness: 0.9, ...}
    aggregate_scores JSONB DEFAULT '{}',
    
    -- Execution metrics
    total_queries INTEGER DEFAULT 0,
    completed_queries INTEGER DEFAULT 0,
    total_latency_ms BIGINT DEFAULT 0,
    total_cost_usd NUMERIC(10, 6) DEFAULT 0,
    
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_evaluations_user_id ON evaluations(user_id);
CREATE INDEX idx_evaluations_pipeline_id ON evaluations(pipeline_id);
CREATE INDEX idx_evaluations_status ON evaluations(status);

-- Composite index for "recent evaluations by pipeline"
CREATE INDEX idx_evaluations_pipeline_created 
    ON evaluations(pipeline_id, created_at DESC);

-- ============================================
-- EVALUATION RESULTS TABLE
-- ============================================
-- Individual query results within an evaluation

CREATE TABLE evaluation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluation_id UUID NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
    
    -- Query details
    query TEXT NOT NULL,
    expected_answer TEXT,
    
    -- Retrieved chunks (array of chunk IDs)
    retrieved_chunk_ids UUID[] DEFAULT '{}',
    
    -- Generated response
    generated_answer TEXT,
    
    -- LLM-as-Judge scores
    -- {context_relevance: 0.9, faithfulness: 0.85, answer_relevance: 0.88, reasoning: "..."}
    scores JSONB DEFAULT '{}',
    
    -- Performance metrics
    latency_ms INTEGER,
    cost_usd NUMERIC(10, 6),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_evaluation_results_evaluation_id 
    ON evaluation_results(evaluation_id);

-- ============================================
-- EXECUTION LOGS TABLE
-- ============================================
-- Stores pipeline execution logs for debugging

CREATE TABLE execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    pipeline_version_id UUID REFERENCES pipeline_versions(id),
    
    -- Which node in the pipeline
    node_id VARCHAR(255),
    node_type VARCHAR(50),
    
    -- Log level: 'info', 'warning', 'error'
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    
    -- Additional context
    details JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_execution_logs_pipeline_id ON execution_logs(pipeline_id);
CREATE INDEX idx_execution_logs_created_at ON execution_logs(created_at DESC);

-- ============================================
-- UPDATED_AT TRIGGER
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER pipelines_updated_at
    BEFORE UPDATE ON pipelines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER test_datasets_updated_at
    BEFORE UPDATE ON test_datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

