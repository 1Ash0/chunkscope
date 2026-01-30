-- ChunkScope Sample Queries with EXPLAIN Plans
-- Demonstrates indexed query performance

-- ============================================
-- 1. FIND ALL PIPELINES BY USER (B-tree index)
-- ============================================
-- Uses: idx_pipelines_user_id

EXPLAIN ANALYZE
SELECT id, name, status, created_at
FROM pipelines
WHERE user_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
ORDER BY created_at DESC
LIMIT 20;

-- Expected plan: Index Scan using idx_pipelines_user_id
-- Estimated cost: O(log n) + O(k) where k = result count

-- ============================================
-- 2. VECTOR SIMILARITY SEARCH (HNSW index)
-- ============================================
-- Uses: idx_chunks_embedding (HNSW)

-- First, set ef_search for accuracy/speed trade-off
SET hnsw.ef_search = 100; -- Higher = more accurate, slower

EXPLAIN ANALYZE
SELECT 
    c.id, 
    c.text, 
    c.metadata,
    1 - (c.embedding <=> '[0.1, 0.2, ...]'::vector(1536)) as similarity
FROM chunks c
WHERE c.document_id = 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'
ORDER BY c.embedding <=> '[0.1, 0.2, ...]'::vector(1536)
LIMIT 10;

-- Expected plan: Index Scan using idx_chunks_embedding
-- HNSW provides approximate nearest neighbor in O(log n)

-- ============================================
-- 3. PAGINATED CHUNKS BY DOCUMENT (B-tree)
-- ============================================
-- Uses: idx_chunks_document_idx

EXPLAIN ANALYZE
SELECT id, text, chunk_index, metadata, token_count
FROM chunks
WHERE document_id = 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'
ORDER BY chunk_index
LIMIT 50 OFFSET 100;

-- Expected plan: Index Scan using idx_chunks_document_idx
-- Efficient cursor-based pagination

-- Better alternative: Keyset pagination (for large offsets)
EXPLAIN ANALYZE
SELECT id, text, chunk_index, metadata, token_count
FROM chunks
WHERE document_id = 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'
  AND chunk_index > 100  -- Last seen chunk_index
ORDER BY chunk_index
LIMIT 50;

-- ============================================
-- 4. EVALUATION HISTORY WITH FILTERS
-- ============================================
-- Uses: idx_evaluations_pipeline_created (composite)

EXPLAIN ANALYZE
SELECT 
    e.id,
    e.name,
    e.status,
    e.aggregate_scores,
    e.total_queries,
    e.created_at
FROM evaluations e
WHERE e.pipeline_id = 'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33'
  AND e.status = 'completed'
ORDER BY e.created_at DESC
LIMIT 10;

-- Expected plan: Index Scan using idx_evaluations_pipeline_created
-- Filter applied on status after index lookup

-- ============================================
-- 5. QUERY NODES BY TYPE (GIN on JSONB)
-- ============================================
-- Uses: idx_pipelines_nodes

EXPLAIN ANALYZE
SELECT id, name, nodes
FROM pipelines
WHERE nodes @> '[{"type": "chunker"}]';

-- Expected plan: Bitmap Index Scan using idx_pipelines_nodes
-- GIN index supports containment operator (@>)

-- ============================================
-- 6. FILTER CHUNKS BY METADATA (GIN on JSONB)
-- ============================================
-- Uses: idx_chunks_metadata

EXPLAIN ANALYZE
SELECT id, text, metadata
FROM chunks
WHERE document_id = 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'
  AND metadata @> '{"page": 5}';

-- Expected plan: Bitmap Index Scan combining:
-- - idx_chunks_document_id (B-tree)
-- - idx_chunks_metadata (GIN)

-- ============================================
-- 7. AGGREGATE EVALUATION METRICS
-- ============================================

EXPLAIN ANALYZE
SELECT 
    p.id,
    p.name,
    COUNT(e.id) as eval_count,
    AVG((e.aggregate_scores->>'avg_context_relevance')::float) as avg_relevance,
    AVG(e.total_latency_ms::float / NULLIF(e.total_queries, 0)) as avg_latency_per_query
FROM pipelines p
LEFT JOIN evaluations e ON e.pipeline_id = p.id AND e.status = 'completed'
WHERE p.user_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
GROUP BY p.id, p.name
ORDER BY avg_relevance DESC NULLS LAST;

-- ============================================
-- 8. CROSS-DOCUMENT SEMANTIC SEARCH
-- ============================================
-- Search across ALL user's documents

EXPLAIN ANALYZE
SELECT 
    c.id,
    c.text,
    d.filename,
    1 - (c.embedding <=> '[0.1, 0.2, ...]'::vector(1536)) as similarity
FROM chunks c
JOIN documents d ON d.id = c.document_id
WHERE d.user_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
ORDER BY c.embedding <=> '[0.1, 0.2, ...]'::vector(1536)
LIMIT 20;

-- This query benefits from:
-- - idx_chunks_embedding (HNSW) for vector search
-- - idx_documents_user_id (B-tree) for user filter
