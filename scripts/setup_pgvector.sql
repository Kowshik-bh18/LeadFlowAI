-- ============================================================
-- LeadFlow AI – pgvector setup migration
-- Run this BEFORE running Django migrations
-- ============================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the database (run as superuser before the rest)
-- CREATE DATABASE leadflow_rag;

-- After running Django migrations, add optimized HNSW index:
-- (Run this after initial data load for best performance)

-- HNSW index for fast approximate nearest-neighbor search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chunk_embedding_hnsw
ON references_documentchunk
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- IVFFlat index (alternative, faster build, slightly less accurate)
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chunk_embedding_ivfflat
-- ON references_documentchunk
-- USING ivfflat (embedding vector_cosine_ops)
-- WITH (lists = 100);

-- Verify extension is installed
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
