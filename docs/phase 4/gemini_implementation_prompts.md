# ChunkScope Phase 4: Gemini 2.0 Flash Thinking Implementation Prompts
## Week-by-Week Detailed Prompts for Automated Variety System

> **Instructions**: Use these prompts sequentially with Gemini 2.0 Flash Thinking (or Gemini 1.5 Pro with extended thinking). Each prompt is self-contained and includes all necessary context.

---

## 📋 Pre-Implementation Setup

**Before starting, ensure you have:**
- [ ] All Phase 4 planning documents in `docs/phase 4/`
- [ ] Phase 3 codebase fully functional
- [ ] Database migrations up to date
- [ ] Development environment running (backend + frontend)

---

## 🚀 Week 1: Preset Library & Document Analyzer

### Prompt 1.1: Create Preset System Backend

```
I'm building ChunkScope, a RAG pipeline visualization tool. I've completed Phase 3 with basic chunking and pipeline builder functionality. Now I need to implement Phase 4: Automated Variety System.

CONTEXT:
- Review the implementation guide at: docs/phase 4/implementation_guide.md
- Review the build plan at: docs/phase 4/updated_build_plan.md
- Current backend tech stack: FastAPI, PostgreSQL + pgvector, Celery, LangChain
- Current backend structure: backend/app/ with models/, api/, services/

TASK: Implement the Preset Library System backend

REQUIREMENTS:
1. Create database migration for presets table (see implementation_guide.md "Database Schema" section)
2. Create the following preset JSON files in backend/app/presets/:
   - legal_document_qa.json
   - customer_support_bot.json
   - code_documentation_search.json
   - medical_records_qa.json
   - academic_research_analysis.json
   - financial_report_analysis.json
   - general_qa.json
   - semantic_search.json
   - chatbot_with_memory.json
   - document_summarization.json
   (Use the JSON format from implementation_guide.md)

3. Implement PresetService class in backend/app/services/preset_service.py with:
   - load_builtin_presets() - Load all JSON presets
   - get_all_presets(category, db) - Fetch from database
   - get_preset_by_id(preset_id, db) - Fetch single preset
   - apply_preset_to_pipeline(preset_id, pipeline_id, user_id, db) - Create pipeline from preset
   - _generate_nodes_from_config(config) - Convert preset to React Flow nodes
   - _generate_edges_from_nodes(nodes) - Create edges between nodes

4. Create API endpoints in backend/app/api/presets.py:
   - GET /api/presets - List all presets (with optional category filter)
   - GET /api/presets/{preset_id} - Get specific preset
   - POST /api/presets/{preset_id}/apply - Apply preset to create pipeline

5. Write pytest tests in tests/test_preset_service.py covering:
   - test_load_builtin_presets() - Verify all 10 presets load correctly
   - test_apply_preset_to_pipeline() - Verify pipeline creation
   - test_preset_api_endpoints() - Test all API endpoints

VALIDATION:
- All 10 preset JSON files are valid and complete
- Database migration runs without errors
- PresetService can load and apply presets
- API endpoints return correct responses
- All tests pass (pytest tests/test_preset_service.py -v)

DELIVERABLES:
- backend/alembic/versions/xxx_add_presets.py
- backend/app/presets/*.json (10 files)
- backend/app/services/preset_service.py
- backend/app/api/presets.py
- backend/app/models.py (updated with Preset model)
- tests/test_preset_service.py

Please implement this following the extended thinking approach from the original implementation_guide.md. Use the exact code structure and patterns shown in the Phase 4 implementation_guide.md.
```

### Prompt 1.2: Create Preset Gallery Frontend

```
CONTEXT:
I've just completed the Preset Library backend (PresetService + API endpoints). Now I need to build the frontend gallery interface.

CURRENT STATE:
- Backend has 10 presets stored in database
- API endpoints working: GET /api/presets, POST /api/presets/{id}/apply
- Frontend tech stack: Next.js, React Flow, TypeScript
- Frontend structure: frontend/src/components/, frontend/src/lib/

TASK: Implement the Preset Gallery UI

REQUIREMENTS:
1. Create PresetGallery component in frontend/src/components/presets/PresetGallery.tsx
   - Grid layout showing preset cards (3 columns on desktop, 2 on tablet, 1 on mobile)
   - Category filter buttons (qa, search, chatbot, analysis, all)
   - Each card displays:
     * Preset name
     * Description
     * Tags (badges)
     * Expected metrics (accuracy range, latency, cost)
     * "Use This Template" button
   - Clicking "Use This Template" calls API and redirects to /pipelines/{id}

2. Create API client functions in frontend/src/lib/api.ts:
   - listPresets(category?: string)
   - getPreset(presetId: string)
   - applyPreset(presetId: string, pipelineId?: string)

3. Create route for preset gallery at frontend/src/app/presets/page.tsx

4. Update navigation to include "Templates" link to /presets

5. Style with modern, premium design:
   - Use shadcn/ui components (Card, Badge, Button)
   - Hover effects on cards
   - Loading states while fetching presets
   - Empty state if no presets found
   - Smooth transitions

VALIDATION:
- Gallery loads all 10 presets in <2 seconds
- Category filtering works correctly
- Clicking "Use This Template" creates pipeline and redirects
- Responsive design works on mobile/tablet/desktop
- Design looks premium and modern

DELIVERABLES:
- frontend/src/components/presets/PresetGallery.tsx
- frontend/src/lib/api.ts (updated)
- frontend/src/app/presets/page.tsx
- frontend/src/components/navigation/* (updated if needed)

Use the exact component structure from implementation_guide.md. Make the UI beautiful and engaging.
```

### Prompt 1.3: Implement Document Analyzer

```
CONTEXT:
Preset library is complete. Now I need to build the Document Analyzer service that analyzes uploaded PDFs and recommends optimal RAG configurations.

CURRENT STATE:
- Backend has PDF processor from Phase 3: backend/app/services/pdf_processor.py
- Need to add intelligent analysis and recommendation engine

TASK: Implement Document Analyzer Service

REQUIREMENTS:
1. Create DocumentAnalyzer class in backend/app/services/document_analyzer.py with:
   - analyze(document_path) -> dict
     * Returns: document_type, structure, density, recommended_config, confidence_score, reasoning
   - _classify_document(text_sample) -> str
     * Use zero-shot classification (facebook/bart-large-mnli) to detect document type
     * Categories: legal, medical, technical, support, academic, financial, general
   - _analyze_structure(pdf_data) -> dict
     * Detect: has_headings, has_tables, has_code_blocks, hierarchy_depth, avg_paragraph_length
   - _analyze_density(text) -> dict
     * Calculate: avg_sentence_length, vocabulary_richness, technical_term_density
   - _generate_config(doc_type, structure, density) -> dict
     * Rule-based config generation (see implementation_guide.md for rules)
   - _explain_recommendation(doc_type, structure, density, config) -> str
     * Generate human-readable explanation

2. Add dependencies to requirements.txt:
   - transformers
   - torch (or install separately)

3. Create API endpoint in backend/app/api/analysis.py:
   - POST /api/analyze/document (accepts file upload)
     * Saves file temporarily
     * Runs analysis
     * Returns analysis result
     * Cleans up temp file

4. Write tests in tests/test_document_analyzer.py:
   - test_analyze_legal_document() - Use tests/fixtures/sample_contract.pdf
   - test_analyze_code_documentation() - Use tests/fixtures/technical_docs.pdf
   - test_analyze_general_content() - Use tests/fixtures/blog_post.pdf
   - test_analyzer_api_endpoint() - Test API with file upload

5. Create test fixtures:
   - tests/fixtures/sample_contract.pdf (legal document)
   - tests/fixtures/technical_docs.pdf (code documentation)
   - tests/fixtures/blog_post.pdf (general content)

VALIDATION:
- DocumentAnalyzer correctly classifies different document types
- Structure and density analysis is accurate
- Recommended configs are appropriate for document types
- Analysis completes in <3 seconds per document
- API endpoint works with file uploads
- All tests pass

DELIVERABLES:
- backend/app/services/document_analyzer.py
- backend/app/api/analysis.py
- backend/requirements.txt (updated)
- tests/test_document_analyzer.py
- tests/fixtures/*.pdf (3 sample PDFs)

Follow the exact implementation from implementation_guide.md. Use efficient processing to keep analysis under 3 seconds.
```

### Prompt 1.4: Week 1 Integration & Testing

```
CONTEXT:
I've completed:
- Preset Library backend + frontend
- Document Analyzer backend

TASK: Week 1 Integration Testing & Polish

REQUIREMENTS:
1. Run full test suite:
   - pytest tests/test_preset_service.py -v
   - pytest tests/test_document_analyzer.py -v
   - Fix any failing tests

2. Manual validation checklist (from validation_prompts.md):
   - Open http://localhost:3000/presets
   - Verify all 10 presets display correctly
   - Test category filtering
   - Apply a preset and verify pipeline creation
   - Upload legal PDF to analyzer and verify recommendations
   - Upload technical PDF and verify different recommendations

3. Create Week 1 completion report:
   - List all implemented features
   - Test results summary
   - Screenshots of preset gallery
   - Any blockers or issues discovered

4. Code cleanup:
   - Remove debug print statements
   - Add docstrings to all public methods
   - Format code (black, prettier)
   - Commit changes with clear commit messages

VALIDATION:
- All automated tests pass (100% success rate)
- Manual testing checklist complete
- No console errors in browser
- No Python exceptions in server logs
- Code is clean and documented

DELIVERABLES:
- Test report document
- Screenshots of working features
- Clean git commits
- Updated task.md marking Week 1 complete
```

---

## 🚀 Week 2: Chunking & Embedding Variety

### Prompt 2.1: Implement Additional Chunking Methods

```
CONTEXT:
Phase 3 already has RecursiveChunker and SemanticChunker. I need to add 4 more chunking methods for variety.

CURRENT STATE:
- Existing: backend/app/services/chunkers/recursive_chunker.py
- Existing: backend/app/services/chunkers/semantic_chunker.py
- Base chunker interface established

TASK: Implement 4 Additional Chunking Methods

REQUIREMENTS:
1. Create SentenceWindowChunker in backend/app/services/chunkers/sentence_window_chunker.py:
   - Parameters: window_size (number of sentences per chunk)
   - Creates overlapping windows of sentences
   - Preserves sentence boundaries
   - Returns chunks with start/end positions

2. Create ParagraphChunker in backend/app/services/chunkers/paragraph_chunker.py:
   - Splits on paragraph boundaries (double newlines)
   - Combines small paragraphs if needed
   - Preserves paragraph structure
   - Respects max_chunk_size parameter

3. Create CodeAwareChunker in backend/app/services/chunkers/code_aware_chunker.py:
   - Detects code blocks (fenced with ```)
   - Keeps code blocks intact
   - Uses tree-sitter or regex for function/class detection
   - Preserves code structure and indentation

4. Create HeadingBasedChunker in backend/app/services/chunkers/heading_based_chunker.py:
   - Detects markdown headings (#, ##, ###)
   - Creates chunks per section
   - Maintains heading hierarchy
   - Each chunk includes its heading

5. Update chunker factory/registry in backend/app/services/chunkers/__init__.py:
   - get_chunker(method: str, config: dict) -> BaseChunker
   - Maps method names to chunker classes

6. Write comprehensive tests in tests/test_chunking_methods.py:
   - test_sentence_window_chunker()
   - test_paragraph_chunker()
   - test_code_aware_chunker()
   - test_heading_based_chunker()
   - Use common SAMPLE_TEXT with varied content (prose, code, headings)

7. Update frontend ChunkerNode component to show all 6 methods in dropdown

VALIDATION:
- All 6 chunking methods work correctly
- Each respects its specific boundary rules
- Tests pass for all methods
- Frontend dropdown shows all options
- Preview updates when switching methods

DELIVERABLES:
- backend/app/services/chunkers/sentence_window_chunker.py
- backend/app/services/chunkers/paragraph_chunker.py
- backend/app/services/chunkers/code_aware_chunker.py
- backend/app/services/chunkers/heading_based_chunker.py
- backend/app/services/chunkers/__init__.py (updated)
- tests/test_chunking_methods.py
- frontend/src/components/nodes/ChunkerNode.tsx (updated)

Follow the patterns from existing chunkers. Ensure each chunker returns consistent format.
```

### Prompt 2.2: Implement Multiple Embedding Providers

```
CONTEXT:
Phase 3 has OpenAI embeddings. I need to add 4 more embedding providers for variety and cost optimization.

CURRENT STATE:
- Existing: backend/app/services/embeddings/openai_embedder.py
- Need to add: Cohere, Voyage AI, Jina AI, Local HuggingFace

TASK: Implement 4 Additional Embedding Providers

REQUIREMENTS:
1. Create embedding provider interface in backend/app/services/embeddings/base.py:
   - BaseEmbedder abstract class
   - Methods: embed(texts: List[str]) -> List[List[float]]
   - Properties: model_name, dimensions, cost_per_million_tokens

2. Create CohereEmbedder in backend/app/services/embeddings/cohere_embedder.py:
   - Use Cohere API
   - Models: embed-english-v3.0, embed-multilingual-v3.0
   - Async implementation
   - Batch processing (up to 96 texts per batch)

3. Create VoyageEmbedder in backend/app/services/embeddings/voyage_embedder.py:
   - Use Voyage AI API
   - Models: voyage-2, voyage-code-2
   - Specialized for technical content

4. Create JinaEmbedder in backend/app/services/embeddings/jina_embedder.py:
   - Use Jina AI API
   - Models: jina-embeddings-v2-base-en
   - Long context support (8192 tokens)

5. Create LocalHuggingFaceEmbedder in backend/app/services/embeddings/local_embedder.py:
   - Use sentence-transformers library
   - Models: BAAI/bge-large-en-v1.5, all-MiniLM-L6-v2
   - Local inference (no API costs)
   - GPU support if available

6. Create EmbeddingCostCalculator in backend/app/services/cost_calculator.py:
   - calculate(provider, model, tokens) -> float
   - Pricing data for all providers
   - Returns cost in USD

7. Update requirements.txt with:
   - cohere
   - voyageai
   - jinaai
   - sentence-transformers

8. Write tests in tests/test_embedding_providers.py:
   - test_openai_embedder()
   - test_cohere_embedder()
   - test_voyage_embedder()
   - test_jina_embedder()
   - test_local_embedder()
   - test_embedding_cost_calculator()

9. Update frontend EmbeddingNode component:
   - Provider dropdown (OpenAI, Cohere, Voyage, Jina, Local)
   - Model dropdown (changes based on provider)
   - Real-time cost estimate display
   - Dimensions display

VALIDATION:
- All 5 embedding providers work
- Cost calculator shows accurate estimates
- Local embedder works without API key
- Frontend shows all providers correctly
- Batch processing is efficient
- All tests pass

DELIVERABLES:
- backend/app/services/embeddings/base.py
- backend/app/services/embeddings/cohere_embedder.py
- backend/app/services/embeddings/voyage_embedder.py
- backend/app/services/embeddings/jina_embedder.py
- backend/app/services/embeddings/local_embedder.py
- backend/app/services/cost_calculator.py
- backend/requirements.txt (updated)
- tests/test_embedding_providers.py
- frontend/src/components/nodes/EmbeddingNode.tsx (updated)

Ensure all embedders follow the same interface. Handle API errors gracefully.
```

### Prompt 2.3: Add Real-Time Chunking Preview

```
CONTEXT:
Multiple chunking methods are implemented. Now I need a real-time preview showing how different methods chunk the same text.

CURRENT STATE:
- 6 chunking methods available
- Pipeline builder has ChunkerNode component
- PDF processor can extract text

TASK: Implement Real-Time Chunking Preview

REQUIREMENTS:
1. Create ChunkingPreview component in frontend/src/components/preview/ChunkingPreview.tsx:
   - Text input area (or file upload)
   - Method selector dropdown
   - Parameter controls (dynamic based on method)
   - Preview panel showing:
     * Chunk boundaries highlighted
     * Chunk count
     * Avg chunk size
     * Min/max sizes
   - Side-by-side comparison mode (compare 2 methods)

2. Create preview API endpoint in backend/app/api/preview.py:
   - POST /api/preview/chunking
     * Accepts: text, method, parameters
     * Returns: chunks with metadata, statistics
     * Fast response (<500ms for typical document)

3. Add visual highlighting:
   - Different colors for different chunks
   - Hover to see chunk metadata
   - Click to select chunk
   - Show character positions

4. Add statistics panel:
   - Total chunks created
   - Average chunk size
   - Size distribution histogram
   - Overlap visualization (for overlapping methods)

5. Integrate into pipeline builder:
   - "Preview" button on ChunkerNode
   - Opens modal with ChunkingPreview
   - Uses current node configuration
   - Can update node parameters from preview

VALIDATION:
- Preview updates instantly when changing parameters
- All 6 chunking methods work in preview
- Highlighting is clear and accurate
- Comparison mode shows meaningful differences
- Performance is good (<500ms to preview)

DELIVERABLES:
- frontend/src/components/preview/ChunkingPreview.tsx
- backend/app/api/preview.py
- frontend/src/components/nodes/ChunkerNode.tsx (updated with preview button)
- CSS styling for chunk highlighting

Make the preview visually engaging and informative. Use smooth animations.
```

### Prompt 2.4: Week 2 Integration & Testing

```
CONTEXT:
I've completed:
- 6 chunking methods (2 existing + 4 new)
- 5 embedding providers (1 existing + 4 new)
- Real-time chunking preview
- Cost calculator

TASK: Week 2 Integration Testing & Polish

REQUIREMENTS:
1. Run full test suite:
   - pytest tests/test_chunking_methods.py -v
   - pytest tests/test_embedding_providers.py -v
   - Fix any failing tests

2. Manual validation (from validation_prompts.md):
   - Test each chunking method with sample documents
   - Verify preview shows correct chunk boundaries
   - Test each embedding provider (ensure API keys configured)
   - Verify cost calculator accuracy
   - Test comparison mode in preview

3. Performance testing:
   - Chunking preview responds in <500ms
   - Embedding generation is reasonably fast
   - Local embedder works on CPU

4. Create comprehensive Week 2 report:
   - Feature list with screenshots
   - Performance metrics
   - Cost comparison table for embeddings
   - Any issues or limitations discovered

5. Documentation:
   - Add docstrings to all new classes/methods
   - Update README with new chunking methods
   - Document embedding provider requirements (API keys)

VALIDATION:
- All tests pass
- Manual validation complete
- Performance meets requirements
- Documentation is clear

DELIVERABLES:
- Week 2 completion report
- Screenshots of preview functionality
- Performance test results
- Updated documentation
- Git commits
```

---

## 🚀 Week 3: Retrieval, Reranking & Query Augmentation

### Prompt 3.1: Implement Hybrid Search Retrieval

```
CONTEXT:
Current system only has basic vector similarity search. I need to implement hybrid search combining vector and keyword (BM25) retrieval.

CURRENT STATE:
- Existing vector search in backend/app/services/retrievers/
- PostgreSQL with pgvector extension installed
- Need to add BM25/keyword search capability

TASK: Implement Hybrid Search System

REQUIREMENTS:
1. Add BM25 search support:
   - Install rank_bm25 package (or implement in PostgreSQL)
   - Create inverted index for keyword search
   - Add full-text search column to chunks table

2. Create HybridRetriever in backend/app/services/retrievers/hybrid_retriever.py:
   - __init__(alpha: float = 0.7)  # 0.7 = 70% vector, 30% keyword
   - retrieve(query: str, top_k: int) -> List[dict]
   - Methods:
     * _vector_search(query, top_n) -> results with vector scores
     * _keyword_search(query, top_n) -> results with BM25 scores
     * _normalize_scores(results) -> normalized 0-1 scores
     * combine_results(vector_results, keyword_results, top_k) -> fused results
   - Use Reciprocal Rank Fusion (RRF) or weighted score combination

3. Implement MMRRetriever (Maximal Marginal Relevance):
   - backend/app/services/retrievers/mmr_retriever.py
   - Reduces redundancy in results
   - Parameters: lambda_mult (diversity factor), top_k

4. Implement ParentDocumentRetriever:
   - backend/app/services/retrievers/parent_document_retriever.py
   - Retrieves small chunks but returns larger parent context
   - Maintains parent-child chunk relationships

5. Update database schema:
   - Add migration for full-text search indexes
   - Add parent_chunk_id field to chunks table
   - Create GIN indexes for text search

6. Create retrieval API enhancement:
   - Update /api/query endpoint to support:
     * retrieval_method: "vector", "keyword", "hybrid", "mmr", "parent_document"
     * alpha parameter for hybrid search
     * lambda_mult for MMR

7. Write tests in tests/test_hybrid_search.py:
   - test_hybrid_search_combines_results()
   - test_alpha_parameter_effect()
   - test_mmr_reduces_redundancy()
   - test_parent_document_retriever()

8. Update frontend RetrievalNode:
   - Algorithm selector dropdown
   - Alpha slider (0.0 - 1.0) for hybrid search
   - Lambda slider for MMR
   - Top K parameter

VALIDATION:
- Hybrid search successfully combines vector + keyword results
- Alpha parameter controls blend ratio
- MMR shows improved diversity
- Parent document retriever returns fuller context
- All tests pass

DELIVERABLES:
- backend/app/services/retrievers/hybrid_retriever.py
- backend/app/services/retrievers/mmr_retriever.py
- backend/app/services/retrievers/parent_document_retriever.py
- backend/alembic/versions/xxx_add_fulltext_search.py
- tests/test_hybrid_search.py
- frontend/src/components/nodes/RetrievalNode.tsx (updated)
- backend/requirements.txt (updated with rank-bm25)

Implement efficient fusion algorithms. Hybrid should be faster than running both separately.
```

### Prompt 3.2: Implement Reranking Methods

```
CONTEXT:
Retrieval is working but initial results need reranking for better accuracy. I need to implement Cohere Rerank API and local cross-encoder reranking.

CURRENT STATE:
- Retrieval returns top N candidates (usually 10-20)
- Need to rerank to top K final results (usually 3-5)
- Should improve accuracy by 15-20%

TASK: Implement Reranking System

REQUIREMENTS:
1. Create base reranker interface in backend/app/services/rerankers/base.py:
   - BaseReranker abstract class
   - Method: rerank(query: str, documents: List[dict], top_k: int) -> List[dict]

2. Create CohereReranker in backend/app/services/rerankers/cohere_reranker.py:
   - Use Cohere Rerank API (rerank-english-v3.0)
   - Async implementation
   - Parameters:
     * model: rerank-english-v3.0 or rerank-multilingual-v3.0
     * top_n: number of candidates to send (default 20)
     * return_k: number to return (default 5)
   - Add rerank_score to results
   - Sort by rerank score descending

3. Create CrossEncoderReranker in backend/app/services/rerankers/cross_encoder_reranker.py:
   - Use sentence-transformers CrossEncoder
   - Models: 
     * cross-encoder/ms-marco-MiniLM-L-12-v2 (fast, decent)
     * cross-encoder/ms-marco-TinyBERT-L-2-v2 (fastest)
     * cross-encoder/ms-marco-electra-base (best accuracy)
   - Local inference (no API calls)
   - Batch processing for efficiency

4. Create RecipRocalRankFusionReranker:
   - backend/app/services/rerankers/rrf_reranker.py
   - Combines rankings from multiple retrievers
   - No ML model needed, pure algorithmic

5. Add reranking step to pipeline:
   - New RerankingNode in backend/app/models.py
   - POST /api/rerank endpoint
   - Accepts: query, documents, method, parameters

6. Write tests in tests/test_reranking.py:
   - test_cohere_reranker()
   - test_cross_encoder_reranker()
   - test_reranking_improves_accuracy()
   - Use sample queries with known relevant/irrelevant docs

7. Update frontend:
   - Create RerankingNode component
   - Provider selector (Cohere, Cross-Encoder, RRF)
   - Model selector (for cross-encoder)
   - Top N / Return K parameters
   - Before/after comparison visualization

8. Add to pipeline builder:
   - RerankingNode can be dragged between retrieval and generation
   - Shows expected accuracy boost
   - Displays latency cost

VALIDATION:
- Cohere reranking works with API key
- Cross-encoder works locally
- Reranking demonstrably improves result relevance
- Latency is acceptable (<500ms for 20 docs)
- All tests pass

DELIVERABLES:
- backend/app/services/rerankers/base.py
- backend/app/services/rerankers/cohere_reranker.py
- backend/app/services/rerankers/cross_encoder_reranker.py
- backend/app/services/rerankers/rrf_reranker.py
- backend/app/api/rerank.py
- tests/test_reranking.py
- frontend/src/components/nodes/RerankingNode.tsx
- backend/requirements.txt (updated)

Ensure reranking integrates smoothly into pipeline execution flow.
```

### Prompt 3.3: Implement Query Augmentation Methods

```
CONTEXT:
Retrieval and reranking are working. Now I need query augmentation techniques to improve retrieval quality by generating better queries.

CURRENT STATE:
- Single query goes to retrieval
- Need: multi-query, HyDE, query expansion

TASK: Implement Query Augmentation System

REQUIREMENTS:
1. Create MultiQueryRetriever in backend/app/services/retrievers/multi_query_retriever.py:
   - Generate 3-5 variations of the user's query using LLM
   - Retrieve documents for each query variant
   - Combine results using RRF
   - Example:
     * Original: "What are the payment terms?"
     * Variant 1: "How should payments be made according to contract?"
     * Variant 2: "What is the payment schedule?"
     * Variant 3: "When are payments due?"

2. Create HyDERetriever (Hypothetical Document Embeddings):
   - backend/app/services/retrievers/hyde_retriever.py
   - Generate hypothetical answer using LLM
   - Embed the hypothetical answer
   - Search using hypothetical answer embedding
   - Often more effective than query embedding

3. Create QueryExpansionRetriever:
   - backend/app/services/retrievers/query_expansion_retriever.py
   - Add synonyms and related terms to query
   - Use WordNet or LLM for expansion
   - Improves keyword search component

4. Create query augmentation service:
   - backend/app/services/query_augmentor.py
   - augment_multi_query(query: str, num_variants: int) -> List[str]
   - augment_hyde(query: str) -> str
   - augment_expansion(query: str) -> str

5. Add LLM integration:
   - Use OpenAI API for query generation
   - Add caching to avoid redundant API calls
   - Fallback if API fails

6. Update retrieval pipeline:
   - Allow selecting augmentation method in RetrievalNode
   - Show generated variants in UI (for debugging)
   - Track which variant retrieved which document

7. Write tests in tests/test_query_augmentation.py:
   - test_multi_query_generation()
   - test_hyde_generation()
   - test_query_expansion()
   - test_augmented_retrieval_improves_results()

8. Update frontend RetrievalNode:
   - Add "Query Augmentation" section
   - Checkboxes: Multi-Query, HyDE, Expansion
   - Show generated queries in dev mode
   - Visual indicator when augmentation is active

VALIDATION:
- Multi-query generates diverse relevant variants
- HyDE creates realistic hypothetical answers
- Query expansion adds useful terms
- Augmented retrieval finds more relevant documents
- Minimal latency impact (<1s added)
- All tests pass

DELIVERABLES:
- backend/app/services/retrievers/multi_query_retriever.py
- backend/app/services/retrievers/hyde_retriever.py
- backend/app/services/retrievers/query_expansion_retriever.py
- backend/app/services/query_augmentor.py
- tests/test_query_augmentation.py
- frontend/src/components/nodes/RetrievalNode.tsx (updated)

Ensure LLM prompts produce high-quality query variants. Cache aggressively.
```

### Prompt 3.4: Week 3 Integration & Testing

```
CONTEXT:
I've completed:
- Hybrid search (vector + keyword)
- MMR and Parent Document retrievers
- Cohere and Cross-Encoder reranking
- Multi-query, HyDE, and query expansion

TASK: Week 3 Integration Testing & Validation

REQUIREMENTS:
1. Run full test suite:
   - pytest tests/test_hybrid_search.py -v
   - pytest tests/test_reranking.py -v
   - pytest tests/test_query_augmentation.py -v
   - Fix all failing tests

2. Manual validation (from validation_prompts.md):
   - Test hybrid search with alpha variations
   - Compare reranked vs non-reranked results
   - Test multi-query with diverse queries
   - Verify HyDE improves retrieval
   - Measure accuracy improvements

3. Accuracy evaluation:
   - Create small evaluation dataset (10-20 queries with labeled relevant docs)
   - Compare retrieval methods:
     * Vector only
     * Hybrid
     * Hybrid + Reranking
     * Hybrid + Multi-Query + Reranking
   - Calculate recall@5, precision@5
   - Document accuracy gains

4. Performance profiling:
   - Measure latency for each component
   - Identify bottlenecks
   - Optimize slow operations
   - Target: <2s total for query → reranked results

5. Create Week 3 completion report:
   - Feature summary with examples
   - Accuracy evaluation results
   - Performance benchmarks
   - Recommendations for users (when to use which method)

VALIDATION:
- All tests pass (100%)
- Accuracy improved by 15%+ with reranking
- Hybrid search outperforms vector-only
- Query augmentation shows measurable benefit
- Performance is acceptable

DELIVERABLES:
- Week 3 completion report
- Accuracy evaluation results (CSV or JSON)
- Performance benchmarks
- Updated documentation
- Git commits
```

---

## 🚀 Week 4: Configuration Wizard & Recommendation Engine

### Prompt 4.1: Implement Configuration Wizard Frontend

```
CONTEXT:
All RAG techniques are implemented. Now I need a guided wizard to help users create optimal pipelines without RAG expertise.

CURRENT STATE:
- 10 presets available
- Document analyzer working
- All RAG techniques implemented
- Need: 4-step wizard for non-experts

TASK: Implement Configuration Wizard UI

REQUIREMENTS:
1. Create ConfigurationWizard component in frontend/src/components/wizard/ConfigurationWizard.tsx:
   - Multi-step form (4 steps)
   - Progress indicator at top
   - Back/Next navigation
   - State management (React useState or useReducer)

2. Implement Step 1: Use Case Selection
   - 4 large cards with icons:
     * Question Answering (❓)
     * Semantic Search (🔍)
     * Chatbot (💬)
     * Document Analysis (📊)
   - Click to select and auto-advance to step 2

3. Implement Step 2: Document Type Selection
   - 6 options in grid:
     * Legal (contracts, briefs)
     * Medical (records, research)
     * Technical (docs, code)
     * Customer Support (FAQs)
     * Academic (papers, books)
     * General Content
   - Click to select and advance

4. Implement Step 3: Priority Selection
   - 4 cards with descriptions:
     * Accuracy First (best results, higher cost)
     * Speed First (fast responses, lower accuracy)
     * Cost First (budget-conscious, local models)
     * Balanced (good mix)
   - Shows trade-offs clearly

5. Implement Step 4: Expertise Level
   - 3 options:
     * Beginner (use preset as-is, no customization)
     * Intermediate (allow some tweaking)
     * Expert (full manual control)
   - Final selection triggers pipeline generation

6. Add visual design:
   - Modern, step-by-step flow
   - Smooth transitions between steps
   - Clear visual hierarchy
   - Loading state while generating config
   - Success animation on completion

7. Create wizard route:
   - /wizard page
   - Add "Quick Start" button on homepage
   - Add to main navigation

8. Handle completion:
   - Call backend wizard API
   - Create pipeline from config
   - Redirect to pipeline editor
   - Show success message

VALIDATION:
- Wizard flows smoothly through 4 steps
- Back button works correctly
- Visual design is clear and engaging
- User can complete wizard in <2 minutes
- Generates appropriate config based on selections

DELIVERABLES:
- frontend/src/components/wizard/ConfigurationWizard.tsx
- frontend/src/app/wizard/page.tsx
- CSS/styling for wizard
- Updated navigation

Make the wizard feel guided and confidence-inspiring for beginners.
```

### Prompt 4.2: Implement Wizard Backend & Rule Engine

```
CONTEXT:
Wizard frontend is complete. Now I need the backend logic to convert wizard inputs into optimal pipeline configurations.

CURRENT STATE:
- Frontend sends wizard state: {useCase, documentType, priority, expertise}
- Need to map to preset selection and config adjustments

TASK: Implement Wizard Backend & Rule Engine

REQUIREMENTS:
1. Create WizardService in backend/app/services/wizard_service.py:
   - generate_config(wizard_state: dict) -> dict
     * Returns: {configuration, preset_id, customization_allowed, reasoning}
   - _select_base_preset(use_case, doc_type) -> preset_id
   - _adjust_for_priority(config, priority) -> config
   - _set_customization_level(expertise) -> bool

2. Implement preset mapping logic:
   - Map (use_case, doc_type) combinations to preset IDs
   - Example mappings:
     * (qa, legal) → legal_document_qa
     * (chatbot, support) → customer_support_bot
     * (search, technical) → code_documentation_search
   - Fallback to general_qa if no specific match

3. Implement priority adjustments:
   - Priority = "accuracy":
     * Use largest embedding models
     * Enable reranking
     * Use hybrid search
   - Priority = "speed":
     * Use small/fast embedding models
     * Disable reranking
     * Use simple vector search
   - Priority = "cost":
     * Use local embedding models
     * Disable expensive API calls
     * Minimal pipeline complexity
   - Priority = "balanced":
     * Medium-sized models
     * Conditional reranking
     * Hybrid search

4. Create API endpoint in backend/app/api/wizard.py:
   - POST /api/wizard/generate
     * Accepts wizard state
     * Returns generated config
     * Creates pipeline if requested
     * Returns pipeline ID

5. Write tests in tests/test_wizard_service.py:
   - test_wizard_legal_qa_accuracy()
   - test_wizard_support_chatbot_cost()
   - test_wizard_technical_search_speed()
   - test_wizard_balanced_config()
   - Verify each combination produces appropriate config

6. Add reasoning explanations:
   - Generate human-readable explanation
   - Example: "Selected Legal QA preset optimized for accuracy. Using large embeddings and Cohere reranking for maximum precision. Estimated cost: $0.10 per 1000 queries."

VALIDATION:
- Wizard generates sensible configs for all input combinations
- Priority adjustments work correctly
- Reasoning is clear and helpful
- All tests pass
- API endpoint works correctly

DELIVERABLES:
- backend/app/services/wizard_service.py
- backend/app/api/wizard.py
- tests/test_wizard_service.py

Ensure rule engine is maintainable and easy to extend with new mappings.
```

### Prompt 4.3: Implement Real-Time Recommendation Engine

```
CONTEXT:
Users can create pipelines manually, from presets, or via wizard. Now I need a recommendation engine that provides real-time suggestions as they build.

CURRENT STATE:
- Manual pipeline builder working
- All RAG techniques available
- Need: smart suggestions during manual editing

TASK: Implement Real-Time Recommendation System

REQUIREMENTS:
1. Create RecommendationEngine in backend/app/services/recommendation_engine.py:
   - analyze_pipeline(pipeline: dict) -> List[dict]
     * Analyzes current pipeline configuration
     * Returns list of recommendations
   - Each recommendation:
     * type: "warning", "suggestion", "optimization", "info"
     * title: Short description
     * message: Detailed explanation
     * action: Optional auto-fix action

2. Implement recommendation rules:
   - Configuration issues:
     * Large chunks + small embeddings → suggest larger embeddings
     * No reranking on high-stakes domain → suggest adding reranking
     * Expensive embedding + cost-sensitive → suggest local alternative
   - Best practices:
     * Legal/medical docs without hybrid search → suggest hybrid
     * Code docs without code-aware chunking → suggest code-aware
     * High chunk overlap without justification → suggest review
   - Optimizations:
     * Duplicate processing steps → suggest consolidation
     * Redundant retrievers → suggest simplified approach
     * Over-engineered for simple use case → suggest simpler config

3. Create API endpoint:
   - POST /api/recommendations/analyze
     * Accepts pipeline configuration
     * Returns recommendations
     * Fast (<200ms)

4. Update frontend pipeline editor:
   - Add recommendations panel (sidebar or bottom panel)
   - Show recommendations with icons (⚠️ warning, 💡 suggestion, ⚡ optimization)
   - Toast notifications for critical issues
   - Click recommendation to apply auto-fix (if available)
   - Real-time updates as user edits pipeline

5. Add recommendation triggers:
   - On node add/remove
   - On configuration change
   - Debounced (500ms delay) to avoid excessive API calls

6. Create notification service:
   - frontend/src/lib/notifications.ts
   - Toast notifications using sonner or react-hot-toast
   - Different styles for different recommendation types

7. Write tests in tests/test_recommendation_engine.py:
   - test_recommend_reranking_for_legal()
   - test_warn_large_chunks_small_embeddings()
   - test_suggest_hybrid_search()
   - test_cost_optimization_suggestions()

VALIDATION:
- Recommendations are relevant and helpful
- No false positives or annoying suggestions
- Real-time updates work smoothly
- Auto-fix actions work correctly
- All tests pass

DELIVERABLES:
- backend/app/services/recommendation_engine.py
- backend/app/api/recommendations.py
- tests/test_recommendation_engine.py
- frontend/src/components/pipeline/RecommendationsPanel.tsx
- frontend/src/lib/notifications.ts
- frontend/src/app/pipelines/[id]/page.tsx (updated)

Make recommendations genuinely helpful, not annoying. Avoid recommendation fatigue.
```

### Prompt 4.4: Week 4 Integration, Testing & Phase 4 Completion

```
CONTEXT:
I've completed all Phase 4 features:
- Preset library (10+ presets)
- Document analyzer
- 6 chunking methods
- 5 embedding providers
- Hybrid search, reranking, query augmentation
- Configuration wizard
- Recommendation engine

TASK: Final Integration, Testing & Phase 4 Sign-Off

REQUIREMENTS:
1. Run complete test suite:
   - pytest tests/ -v --tb=short
   - Fix all failing tests
   - Aim for >90% code coverage
   - Generate coverage report

2. Run integration tests:
   - pytest tests/integration/test_automated_variety_e2e.py -v
   - Test complete user flows:
     * Preset application → execution → query
     * Wizard flow → pipeline creation → execution
     * Manual build → recommendations → optimization

3. Complete manual validation checklist (validation_prompts.md):
   - User Acceptance Criteria (all 7 items)
   - Component ratings (7 components)
   - Calculate overall Phase 4 rating

4. Performance testing:
   - Preset application: <2s
   - Document analysis: <3s
   - Wizard completion: <2 minutes total UX time
   - Config generation: <1s
   - Full query (chunking → retrieval → reranking): <3s

5. Create comprehensive Phase 4 completion report:
   - Executive summary
   - All features implemented (with screenshots)
   - Test results (all automated tests)
   - Validation checklist results
   - Performance benchmarks
   - Accuracy improvements demonstrated
   - Known limitations or future improvements
   - User documentation (how to use new features)

6. Update all documentation:
   - README.md with Phase 4 features
   - API documentation
   - User guide for presets and wizard
   - Developer guide for adding new presets/methods

7. Code cleanup and polish:
   - Remove all debug code
   - Complete all docstrings
   - Format all code (black, prettier)
   - Fix linting issues
   - Optimize imports

8. Git housekeeping:
   - Review all commits
   - Squash WIP commits if needed
   - Write clear commit messages
   - Create Phase 4 completion tag
   - Push to repository

VALIDATION CRITERIA (Must Pass All):
1. ✅ Preset Gallery: User can browse 10+ presets and apply in <30 seconds
2. ✅ Document Upload: User can upload PDF and get recommendations in <5 seconds
3. ✅ Wizard: First-time user can create working pipeline in <3 minutes
4. ✅ Variety: User can choose from 6+ chunking, 5+ embedding options
5. ✅ Hybrid Search: Produces better results than vector-only
6. ✅ Reranking: Improves accuracy by 15%+
7. ✅ End-to-End: Zero to working RAG in <10 minutes

PHASE 4 SUCCESS CRITERIA:
- Overall rating ≥ 7.5/10 (from validation_prompts.md)
- All automated tests pass
- All 7 user acceptance criteria met
- Documentation complete
- Code quality high

DELIVERABLES:
- Phase 4 completion report (comprehensive)
- Test coverage report
- Performance benchmark results
- Updated documentation (README, user guide, API docs)
- Clean git history
- Screenshots/videos of working features
- Recommendations for Phase 5

If rating ≥ 7.5 → Proceed to Phase 5 (Evaluation Framework)
If rating < 7.5 → Document issues and create remediation plan

This marks the completion of Phase 4: Automated Variety System. Take time to ensure quality and completeness before moving to Phase 5.
```

---

## 📋 Post-Week 4: Documentation & Handoff

### Final Prompt: Create User Documentation

```
CONTEXT:
Phase 4 is functionally complete. I need comprehensive user-facing documentation.

TASK: Create User Documentation for Phase 4 Features

REQUIREMENTS:
1. Create docs/user_guide/automated_variety.md:
   - Introduction to automated variety features
   - When to use presets vs wizard vs manual
   - Step-by-step guides:
     * How to use preset gallery
     * How to use configuration wizard
     * How to analyze documents
     * How to build custom pipelines
     * How to interpret recommendations
   - Best practices
   - Troubleshooting common issues

2. Create docs/user_guide/rag_techniques.md:
   - Explanation of all RAG techniques:
     * Chunking methods (when to use each)
     * Embedding providers (comparison table)
     * Retrieval algorithms (hybrid vs vector)
     * Reranking (accuracy vs cost trade-off)
     * Query augmentation (benefits)
   - Configuration guidelines
   - Cost optimization tips

3. Update README.md:
   - Add Phase 4 features section
   - Update screenshots
   - Add "Quick Start" using wizard
   - Link to detailed user guides

4. Create video tutorial script (optional):
   - 5-minute walkthrough of key features
   - Demonstrates preset → wizard → manual flow
   - Shows accuracy improvements

DELIVERABLES:
- docs/user_guide/automated_variety.md
- docs/user_guide/rag_techniques.md
- README.md (updated)
- Optional: video tutorial script

Make documentation clear for non-technical users while providing depth for experts.
```

---

## 🎯 Summary: Using These Prompts

**How to use this document:**

1. **Week 1**: Execute prompts 1.1 → 1.2 → 1.3 → 1.4 sequentially
2. **Week 2**: Execute prompts 2.1 → 2.2 → 2.3 → 2.4 sequentially
3. **Week 3**: Execute prompts 3.1 → 3.2 → 3.3 → 3.4 sequentially
4. **Week 4**: Execute prompts 4.1 → 4.2 → 4.3 → 4.4 sequentially
5. **Post-Week 4**: Create user documentation

**Tips for success:**
- Copy entire prompt including CONTEXT, TASK, REQUIREMENTS, VALIDATION
- Provide Gemini with access to the referenced documents (implementation_guide.md, etc.)
- After each prompt, verify deliverables before proceeding
- If a prompt fails, debug before moving to next prompt
- Keep track of completed items in task.md

**Expected timeline:**
- Week 1: ~20-30 hours (preset system + analyzer)
- Week 2: ~20-30 hours (chunking + embedding variety)
- Week 3: ~25-35 hours (retrieval + reranking + augmentation)
- Week 4: ~15-25 hours (wizard + recommendations + testing)
- **Total**: ~80-120 hours (3-4 weeks full-time)

**Phase 4 complete when:**
- ✅ All prompts executed successfully
- ✅ All tests passing
- ✅ All validation criteria met
- ✅ Overall rating ≥ 7.5/10
- ✅ Documentation complete

→ Then proceed to Phase 5: Evaluation & Comparison Framework
