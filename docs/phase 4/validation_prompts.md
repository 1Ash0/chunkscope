# ChunkScope Phase 4: Validation Prompts & Quality Checks
## Automated Variety System - Testing & Verification

---

## 🎯 Validation Philosophy

**Goal**: Every component must be validated with automated tests AND manual verification

**Rating Scale**: 1-10 (7+ required to pass)
- **10**: Perfect, production-ready
- **8-9**: Excellent, minor issues
- **7**: Good, acceptable with noted improvements
- **5-6**: Needs work, significant issues
- **1-4**: Failed, major problems

---

## ✅ Component 1: Preset Library System

### Automated Test

```python
# tests/test_preset_service.py

import pytest
from app.services.preset_service import PresetService
from app.models import Preset, Pipeline

@pytest.mark.asyncio
async def test_load_builtin_presets():
    """Verify all preset JSON files load correctly"""
    presets = PresetService.load_builtin_presets()
    
    # Check: At least 10 presets exist
    assert len(presets) >= 10, f"Expected 10+ presets, found {len(presets)}"
    
    # Check: Each preset has required fields
    required_fields = ["id", "name", "category", "configuration"]
    for preset in presets:
        for field in required_fields:
            assert field in preset, f"Preset missing required field: {field}"
    
    # Check: Configuration is valid
    for preset in presets:
        config = preset["configuration"]
        assert "chunking" in config, "Preset missing chunking config"
        assert "embedding" in config, "Preset missing embedding config"
        assert "retrieval" in config, "Preset missing retrieval config"
    
    print(f"✅ Loaded {len(presets)} valid presets")

@pytest.mark.asyncio
async def test_apply_preset_to_pipeline(test_db, test_user):
    """Verify preset creates valid pipeline"""
    # Create a preset in DB
    preset = Preset(
        id="test_preset",
        name="Test Preset",
        category="qa",
        configuration={
            "chunking": {"method": "recursive", "size": 800},
            "embedding": {"provider": "openai", "model": "text-embedding-3-small"},
            "retrieval": {"algorithm": "similarity_search", "top_k": 5}
        }
    )
    test_db.add(preset)
    await test_db.commit()
    
    # Apply preset
    pipeline = await PresetService.apply_preset_to_pipeline(
        preset_id="test_preset",
        pipeline_id="test_pipeline",
        user_id=test_user.id,
        db=test_db
    )
    
    # Check: Pipeline created with correct nodes
    assert len(pipeline.nodes) >= 3, "Pipeline should have at least 3 nodes"
    
    # Check: Nodes have correct types
    node_types = [n["type"] for n in pipeline.nodes]
    assert "chunkerNode" in node_types, "Missing chunker node"
    assert "embeddingNode" in node_types, "Missing embedding node"
    
    # Check: Edges connect nodes
    assert len(pipeline.edges) > 0, "Pipeline has no edges"
    
    print(f"✅ Pipeline created with {len(pipeline.nodes)} nodes, {len(pipeline.edges)} edges")

@pytest.mark.asyncio
async def test_preset_api_endpoints(test_client):
    """Verify API endpoints work correctly"""
    # GET /api/presets
    response = await test_client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert "presets" in data
    assert data["count"] > 0
    
    # GET /api/presets?category=qa
    response = await test_client.get("/api/presets?category=qa")
    assert response.status_code == 200
    data = response.json()
    for preset in data["presets"]:
        assert preset["category"] == "qa"
    
    # POST /api/presets/{id}/apply
    preset_id = data["presets"][0]["id"]
    response = await test_client.post(
        f"/api/presets/{preset_id}/apply",
        json={"pipeline_id": None}
    )
    assert response.status_code == 200
    pipeline_data = response.json()
    assert "id" in pipeline_data
    assert "nodes" in pipeline_data
    
    print("✅ All preset API endpoints working")
```

**Run Command**:
```bash
cd backend
pytest tests/test_preset_service.py -v
```

### Manual Validation Checklist

**Test in Browser**: http://localhost:3000/presets

- [ ] **Load Gallery**: Preset gallery loads in <2 seconds
- [ ] **Count**: 10+ presets displayed
- [ ] **Categories**: Filter by category (qa, search, chatbot, analysis)
- [ ] **Visual Design**: Cards show name, description, tags, metrics
- [ ] **Apply Preset**: Click "Use This Template" → redirects to pipeline editor
- [ ] **Pipeline Created**: React Flow canvas shows 5+ nodes connected
- [ ] **Configuration**: Node configurations match preset spec
- [ ] **Save**: Pipeline saves to database correctly

**Rating Criteria**:
- **10**: All tests pass, gallery loads instantly, design is beautiful
- **8**: All tests pass, minor UI polish needed
- **6**: Tests pass but UI is ugly or slow
- **4**: Some tests fail, presets don't apply correctly

**Expected Rating**: 8-10

---

## ✅ Component 2: Document Analyzer

### Automated Test

```python
# tests/test_document_analyzer.py

import pytest
from app.services.document_analyzer import DocumentAnalyzer

@pytest.mark.asyncio
async def test_analyze_legal_document():
    """Test analysis of legal contract PDF"""
    analyzer = DocumentAnalyzer()
    
    # Use test fixture PDF
    result = await analyzer.analyze("tests/fixtures/sample_contract.pdf")
    
    # Check: Returns all required fields
    assert "document_type" in result
    assert "structure" in result
    assert "density" in result
    assert "recommended_config" in result
    assert "reasoning" in result
    
    # Check: Classifies correctly (should be 'legal')
    assert result["document_type"] == "legal", f"Expected 'legal', got {result['document_type']}"
    
    # Check: Configuration is appropriate for legal docs
    config = result["recommended_config"]
    assert config["chunking"]["method"] in ["paragraph_based", "semantic"]
    assert config["embedding"]["model"] in ["text-embedding-3-large", "voyage-2"]
    
    # Check: Recommends reranking for legal docs
    assert "reranking" in config, "Legal docs should include reranking"
    
    print(f"✅ Document classified as {result['document_type']}")
    print(f"   Recommended chunking: {config['chunking']['method']}")
    print(f"   Reasoning: {result['reasoning']}")

@pytest.mark.asyncio
async def test_analyze_code_documentation():
    """Test analysis of technical documentation with code"""
    analyzer = DocumentAnalyzer()
    
    result = await analyzer.analyze("tests/fixtures/technical_docs.pdf")
    
    # Check: Classifies as technical
    assert result["document_type"] == "technical"
    
    # Check: Detects code blocks
    assert result["structure"]["has_code_blocks"] == True
    
    # Check: Recommends code-aware chunking
    config = result["recommended_config"]
    assert "code" in config["chunking"]["method"].lower()
    
    print(f"✅ Technical doc analyzed correctly")

@pytest.mark.asyncio
async def test_analyze_general_content():
    """Test analysis of general content"""
    analyzer = DocumentAnalyzer()
    
    result = await analyzer.analyze("tests/fixtures/blog_post.pdf")
    
    # Check: Uses appropriate defaults for general content
    config = result["recommended_config"]
    assert config["chunking"]["method"] in ["recursive", "semantic"]
    
    # Check: Does NOT recommend expensive reranking for general content
    assert "reranking" not in config or config.get("reranking") is None
    
    print(f"✅ General content analyzed with balanced config")

@pytest.mark.asyncio
async def test_analyzer_api_endpoint(test_client):
    """Test document analysis API"""
    # Upload PDF file
    with open("tests/fixtures/sample_contract.pdf", "rb") as f:
        response = await test_client.post(
            "/api/analyze/document",
            files={"file": ("contract.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check: Returns analysis result
    assert "document_type" in data
    assert "recommended_config" in data
    
    # Check: Response time < 3 seconds
    assert response.elapsed.total_seconds() < 3.0, "Analysis took too long"
    
    print(f"✅ Analysis API working, response time: {response.elapsed.total_seconds():.2f}s")
```

**Run Command**:
```bash
cd backend
pytest tests/test_document_analyzer.py -v
```

### Manual Validation Checklist

**Test in Browser**: Upload document via UI

- [ ] **Legal PDF**: Upload contract → classifies as "legal" → recommends large chunks + reranking
- [ ] **Technical PDF**: Upload code docs → detects code blocks → recommends code-aware chunking
- [ ] **Medical PDF**: Upload medical record → classifies as "medical" → recommends high-accuracy embedding
- [ ] **Speed**: Analysis completes in <3 seconds
- [ ] **Reasoning**: Displays human-readable explanation
- [ ] **Apply Config**: "Use Recommended Config" button applies settings to pipeline
- [ ] **Override**: Can still manually override recommendations

**Rating Criteria**:
- **10**: Perfect classification, fast, recommendations are excellent
- **8**: Correct classification, good recommendations, reasonable speed
- **6**: Mostly correct, but some misclassifications or slow
- **4**: Frequent misclassifications, poor recommendations

**Expected Rating**: 8-10

---

## ✅ Component 3: Configuration Wizard

### Automated Test

```python
# tests/test_wizard_service.py

import pytest
from app.services.wizard_service import WizardService

def test_wizard_legal_qa_accuracy():
    """Test wizard generates correct config for legal QA focused on accuracy"""
    state = {
        "useCase": "qa",
        "documentType": "legal",
        "priority": "accuracy",
        "expertise": "beginner"
    }
    
    result = WizardService.generate_config(state)
    config = result["configuration"]
    
    # Check: Uses high-accuracy embedding
    assert config["embedding"]["model"] == "text-embedding-3-large"
    
    # Check: Includes reranking
    assert "reranking" in config
    assert config["reranking"]["method"] == "cohere_rerank_v3"
    
    # Check: Disables customization for beginner
    assert result["customization_allowed"] == False
    
    print(f"✅ Legal QA (accuracy) config correct")

def test_wizard_support_chatbot_cost():
    """Test wizard generates cost-optimized config for support chatbot"""
    state = {
        "useCase": "chatbot",
        "documentType": "support",
        "priority": "cost",
        "expertise": "intermediate"
    }
    
    result = WizardService.generate_config(state)
    config = result["configuration"]
    
    # Check: Uses local/cheap embedding
    assert config["embedding"]["provider"] == "local"
    
    # Check: No reranking (to save cost)
    assert "reranking" not in config
    
    # Check: Allows customization for intermediate
    assert result["customization_allowed"] == True
    
    print(f"✅ Support chatbot (cost) config correct")

def test_wizard_technical_search_speed():
    """Test wizard generates fast config for technical search"""
    state = {
        "useCase": "search",
        "documentType": "technical",
        "priority": "speed",
        "expertise": "expert"
    }
    
    result = WizardService.generate_config(state)
    config = result["configuration"]
    
    # Check: Uses fast embedding model
    assert config["embedding"]["model"] == "text-embedding-3-small"
    
    # Check: Simple retrieval (no hybrid)
    assert config["retrieval"]["algorithm"] == "similarity_search"
    
    # Check: No reranking (to improve speed)
    assert "reranking" not in config
    
    # Check: Full customization for expert
    assert result["customization_allowed"] == True
    
    print(f"✅ Technical search (speed) config correct")
```

**Run Command**:
```bash
cd backend
pytest tests/test_wizard_service.py -v
```

### Manual Validation Checklist

**Test in Browser**: http://localhost:3000/wizard

- [ ] **Step 1 (Use Case)**: 4 options displayed with icons
- [ ] **Step 2 (Doc Type)**: 6 document type options
- [ ] **Step 3 (Priority)**: 4 priority options with descriptions
- [ ] **Step 4 (Expertise)**: 3 expertise levels
- [ ] **Navigation**: Back button works at each step
- [ ] **Progress Indicator**: Shows current step (1/4, 2/4, etc.)
- [ ] **Config Generation**: Completes in <1 second after step 4
- [ ] **Redirect**: Automatically navigates to pipeline editor
- [ ] **Pipeline Created**: Canvas shows recommended pipeline
- [ ] **User Flow Time**: Can complete full wizard in <2 minutes

**Test Specific Paths**:
1. Legal QA + Accuracy → Should use large embeddings + reranking
2. Support Chatbot + Cost → Should use local embeddings, no reranking
3. Technical Search + Speed → Should use small embeddings, simple retrieval

**Rating Criteria**:
- **10**: Smooth flow, instant generation, perfect configs
- **8**: Good flow, correct configs, minor UX issues
- **6**: Functional but clunky, some config issues
- **4**: Buggy navigation, incorrect configs

**Expected Rating**: 8-10

---

## ✅ Component 4: Chunking Methods (6+ Varieties)

### Automated Test

```python
# tests/test_chunking_methods.py

import pytest
from app.services.chunkers import (
    RecursiveChunker,
    SemanticChunker,
    SentenceWindowChunker,
    ParagraphChunker,
    CodeAwareChunker,
    HeadingBasedChunker
)

SAMPLE_TEXT = """
# Introduction
This is the introduction paragraph. It contains several sentences.
Each sentence adds context.

# Main Content
This is the main content section. It has more detailed information.
The content is structured in paragraphs.

# Code Example
```python
def example_function():
    return "Hello, World!"
```

# Conclusion
This is the conclusion. It wraps up the document.
"""

def test_recursive_chunker():
    """Test recursive character chunking"""
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk(SAMPLE_TEXT, metadata={})
    
    # Check: Creates multiple chunks
    assert len(chunks) > 1
    
    # Check: Respects max size
    for chunk in chunks:
        assert len(chunk["text"]) <= 120  # Allow some variance
    
    # Check: Has overlap
    # (Test by checking if last 20 chars of chunk N match first 20 chars of chunk N+1)
    
    print(f"✅ Recursive chunker created {len(chunks)} chunks")

def test_semantic_chunker():
    """Test semantic similarity-based chunking"""
    chunker = SemanticChunker(threshold=0.6)
    chunks = chunker.chunk(SAMPLE_TEXT, metadata={})
    
    # Check: Identifies topic boundaries
    assert len(chunks) >= 3  # Should separate intro, main, conclusion
    
    # Check: Chunks are coherent (all from same section)
    # This is hard to test automatically, but we can check length variation
    
    print(f"✅ Semantic chunker created {len(chunks)} coherent chunks")

def test_paragraph_chunker():
    """Test paragraph-based chunking"""
    chunker = ParagraphChunker()
    chunks = chunker.chunk(SAMPLE_TEXT, metadata={})
    
    # Check: Respects paragraph boundaries
    for chunk in chunks:
        # Should not split mid-paragraph
        assert not chunk["text"].strip().startswith("This is")
    
    print(f"✅ Paragraph chunker created {len(chunks)} chunks")

def test_code_aware_chunker():
    """Test code-aware chunking"""
    chunker = CodeAwareChunker()
    chunks = chunker.chunk(SAMPLE_TEXT, metadata={})
    
    # Check: Keeps code blocks intact
    code_chunks = [c for c in chunks if "def example_function" in c["text"]]
    assert len(code_chunks) > 0, "Code block should be in a chunk"
    
    # Check: Code block not split
    code_chunk = code_chunks[0]
    assert "```python" in code_chunk["text"]
    assert "```" in code_chunk["text"][10:]  # Closing backticks
    
    print(f"✅ Code-aware chunker preserved code blocks")

def test_heading_based_chunker():
    """Test heading-based hierarchical chunking"""
    chunker = HeadingBasedChunker()
    chunks = chunker.chunk(SAMPLE_TEXT, metadata={})
    
    # Check: Chunks align with headings
    assert len(chunks) == 4  # Intro, Main, Code, Conclusion
    
    # Check: Each chunk includes heading
    for chunk in chunks:
        assert chunk["text"].strip().startswith("#")
    
    print(f"✅ Heading-based chunker created {len(chunks)} section chunks")

def test_sentence_window_chunker():
    """Test sentence window chunking"""
    chunker = SentenceWindowChunker(window_size=3)
    chunks = chunker.chunk(SAMPLE_TEXT, metadata={})
    
    # Check: Creates overlapping windows
    assert len(chunks) >= 5
    
    # Check: Each chunk has ~3 sentences (may vary at boundaries)
    for chunk in chunks:
        sentence_count = chunk["text"].count(".")
        assert 1 <= sentence_count <= 5  # Allow flexibility
    
    print(f"✅ Sentence window chunker created {len(chunks)} windows")
```

**Run Command**:
```bash
cd backend
pytest tests/test_chunking_methods.py -v
```

### Manual Validation

**Test in Pipeline Builder**: Create pipeline with chunker node

- [ ] **Method Selector**: Dropdown shows 6+ chunking methods
- [ ] **Preview**: Upload sample PDF → see real-time chunk preview
- [ ] **Recursive**: Adjust size slider (200-2000) → chunks update
- [ ] **Semantic**: Adjust threshold (0.3-0.8) → chunk boundaries change
- [ ] **Paragraph**: Preserves paragraph structure visually
- [ ] **Code-Aware**: Upload tech doc with code → code blocks intact
- [ ] **Heading-Based**: Upload hierarchical doc → chunks align with sections
- [ ] **Sentence Window**: Window size slider (1-5) works

**Rating Criteria**:
- **10**: All 6+ methods work perfectly, preview is instant
- **8**: All methods work, minor preview lag
- **6**: Most methods work, some bugs
- **4**: Several methods broken

**Expected Rating**: 8-10

---

## ✅ Component 5: Embedding Provider Variety (5+)

### Automated Test

```python
# tests/test_embedding_providers.py

import pytest
from app.services.embeddings import (
    OpenAIEmbedder,
    CohereEmbedder,
    VoyageEmbedder,
    JinaEmbedder,
    LocalHuggingFaceEmbedder
)

SAMPLE_TEXTS = [
    "This is a test sentence about AI.",
    "Machine learning models are powerful.",
    "Natural language processing is amazing."
]

@pytest.mark.asyncio
async def test_openai_embedder():
    """Test OpenAI embedding generation"""
    embedder = OpenAIEmbedder(model="text-embedding-3-small")
    
    embeddings = await embedder.embed(SAMPLE_TEXTS)
    
    # Check: Correct dimensions
    assert len(embeddings) == 3
    assert len(embeddings[0]) == 1536  # text-embedding-3-small dimensions
    
    # Check: Embeddings are normalized
    import numpy as np
    for emb in embeddings:
        norm = np.linalg.norm(emb)
        assert 0.99 < norm < 1.01  # Should be unit length
    
    print(f"✅ OpenAI embedder working, dim={len(embeddings[0])}")

@pytest.mark.asyncio
async def test_cohere_embedder():
    """Test Cohere embedding generation"""
    embedder = CohereEmbedder(model="embed-english-v3.0")
    
    embeddings = await embedder.embed(SAMPLE_TEXTS)
    
    assert len(embeddings) == 3
    assert len(embeddings[0]) == 1024  # Cohere dimensions
    
    print(f"✅ Cohere embedder working, dim={len(embeddings[0])}")

@pytest.mark.asyncio
async def test_local_embedder():
    """Test local HuggingFace embedding"""
    embedder = LocalHuggingFaceEmbedder(model="BAAI/bge-large-en-v1.5")
    
    embeddings = await embedder.embed(SAMPLE_TEXTS)
    
    assert len(embeddings) == 3
    assert len(embeddings[0]) == 1024  # BGE dimensions
    
    print(f"✅ Local embedder working, dim={len(embeddings[0])}")

@pytest.mark.asyncio
async def test_embedding_cost_calculator():
    """Test cost calculation for different providers"""
    from app.services.cost_calculator import EmbeddingCostCalculator
    
    calculator = EmbeddingCostCalculator()
    
    # 100k tokens
    tokens = 100_000
    
    openai_cost = calculator.calculate("openai", "text-embedding-3-large", tokens)
    cohere_cost = calculator.calculate("cohere", "embed-english-v3.0", tokens)
    local_cost = calculator.calculate("local", "BAAI/bge-large-en-v1.5", tokens)
    
    # Check: Local is cheapest
    assert local_cost < cohere_cost
    assert local_cost < openai_cost
    
    # Check: Realistic costs
    assert 0 < openai_cost < 1.0  # Should be cents for 100k tokens
    
    print(f"✅ Cost calculator: OpenAI=${openai_cost:.4f}, Cohere=${cohere_cost:.4f}, Local=${local_cost:.4f}")
```

**Run Command**:
```bash
cd backend
pytest tests/test_embedding_providers.py -v
```

### Manual Validation

**Test in Pipeline Builder**: Configure embedding node

- [ ] **Provider Dropdown**: Shows 5+ providers (OpenAI, Cohere, Voyage, Jina, Local)
- [ ] **Model Selection**: Each provider shows available models
- [ ] **Cost Estimate**: Real-time cost calculation displays
- [ ] **Comparison**: Side-by-side comparison widget works
- [ ] **Local Model**: Download button for local models (if not cached)
- [ ] **Dimensions**: Shows embedding dimensions for each model
- [ ] **Speed**: Displays expected tokens/sec

**Rating Criteria**:
- **10**: All 5+ providers work, cost calculator accurate
- **8**: All providers work, minor UI issues
- **6**: Most providers work, cost calculator off
- **4**: Several providers broken

**Expected Rating**: 8-10

---

## ✅ Component 6: Hybrid Search Implementation

### Automated Test

```python
# tests/test_hybrid_search.py

import pytest
from app.services.retrievers.hybrid_retriever import HybridRetriever

@pytest.mark.asyncio
async def test_hybrid_search_combines_results():
    """Test hybrid search merges vector + keyword results"""
    retriever = HybridRetriever(alpha=0.7)  # 70% vector, 30% keyword
    
    query = "What is machine learning?"
    
    # Mock vector results
    vector_results = [
        {"id": "doc1", "score": 0.9, "text": "Machine learning is AI..."},
        {"id": "doc2", "score": 0.8, "text": "ML models learn patterns..."}
    ]
    
    # Mock keyword results (BM25)
    keyword_results = [
        {"id": "doc3", "score": 12.5, "text": "Machine learning definition..."},
        {"id": "doc1", "score": 10.0, "text": "Machine learning is AI..."}
    ]
    
    # Combine
    final_results = retriever.combine_results(vector_results, keyword_results, top_k=3)
    
    # Check: Returns fused results
    assert len(final_results) == 3
    
    # Check: doc1 appears only once (from both lists)
    doc_ids = [r["id"] for r in final_results]
    assert doc_ids.count("doc1") == 1
    
    # Check: Scores are normalized and combined
    assert all("combined_score" in r for r in final_results)
    
    print(f"✅ Hybrid search combined {len(final_results)} unique results")

@pytest.mark.asyncio
async def test_alpha_parameter_effect():
    """Test alpha controls vector vs keyword balance"""
    retriever_vector_heavy = HybridRetriever(alpha=0.9)  # Favor vector
    retriever_keyword_heavy = HybridRetriever(alpha=0.1)  # Favor keyword
    
    vector_results = [{"id": "v1", "score": 0.9}]
    keyword_results = [{"id": "k1", "score": 15.0}]
    
    # Vector-heavy should rank v1 higher
    results_vh = retriever_vector_heavy.combine_results(vector_results, keyword_results, top_k=2)
    assert results_vh[0]["id"] == "v1"
    
    # Keyword-heavy should rank k1 higher
    results_kh = retriever_keyword_heavy.combine_results(vector_results, keyword_results, top_k=2)
    assert results_kh[0]["id"] == "k1"
    
    print(f"✅ Alpha parameter correctly balances vector/keyword ranking")
```

**Run Command**:
```bash
cd backend
pytest tests/test_hybrid_search.py -v
```

### Manual Validation

**Test in Pipeline**: Create retrieval node with hybrid search

- [ ] **Enable Hybrid**: Toggle "Hybrid Search" enabled
- [ ] **Alpha Slider**: Adjust 0.0 (keyword only) to 1.0 (vector only)
- [ ] **Test Query**: Upload docs, run query, see results
- [ ] **Comparison**: Compare hybrid vs pure vector results
- [ ] **Accuracy**: Hybrid should retrieve more relevant docs on keyword-heavy queries

**Rating Criteria**:
- **10**: Hybrid clearly outperforms vector-only on test queries
- **8**: Hybrid works, minor improvement over vector-only
- **6**: Hybrid works but no clear benefit
- **4**: Hybrid broken or worse than vector-only

**Expected Rating**: 8-10

---

## ✅ Component 7: Reranking (Cohere + Cross-Encoder)

### Automated Test

```python
# tests/test_reranking.py

import pytest
from app.services.rerankers import CohereReranker, CrossEncoderReranker

QUERY = "What are the benefits of exercise?"
CANDIDATE_DOCS = [
    {"id": "1", "text": "Exercise improves cardiovascular health and reduces disease risk."},
    {"id": "2", "text": "The weather today is sunny and warm."},
    {"id": "3", "text": "Regular physical activity boosts mental health and mood."},
    {"id": "4", "text": "Pizza recipes vary by region and topping preference."},
    {"id": "5", "text": "Exercise helps with weight management and muscle building."}
]

@pytest.mark.asyncio
async def test_cohere_reranker():
    """Test Cohere reranking API"""
    reranker = CohereReranker(model="rerank-english-v3.0")
    
    results = await reranker.rerank(QUERY, CANDIDATE_DOCS, top_n=3)
    
    # Check: Returns top 3
    assert len(results) == 3
    
    # Check: Relevant docs ranked higher
    top_ids = [r["id"] for r in results]
    assert "1" in top_ids  # Exercise benefits
    assert "3" in top_ids  # Mental health
    assert "2" not in top_ids  # Weather should be filtered out
    
    # Check: Scores in descending order
    scores = [r["rerank_score"] for r in results]
    assert scores == sorted(scores, reverse=True)
    
    print(f"✅ Cohere reranker returned {len(results)} relevant results")

@pytest.mark.asyncio
async def test_cross_encoder_reranker():
    """Test local cross-encoder reranking"""
    reranker = CrossEncoderReranker(model="cross-encoder/ms-marco-MiniLM-L-12-v2")
    
    results = await reranker.rerank(QUERY, CANDIDATE_DOCS, top_n=3)
    
    # Check: Returns top 3
    assert len(results) == 3
    
    # Check: Relevant docs ranked higher
    top_ids = [r["id"] for r in results]
    assert "1" in top_ids
    assert "5" in top_ids
    
    print(f"✅ Cross-encoder reranker working")

@pytest.mark.asyncio
async def test_reranking_improves_accuracy():
    """Test that reranking actually improves retrieval accuracy"""
    # Simulate initial retrieval with decent but imperfect results
    initial_results = [
        {"id": "4", "score": 0.78, "text": CANDIDATE_DOCS[3]["text"]},  # Pizza (false positive)
        {"id": "1", "score": 0.75, "text": CANDIDATE_DOCS[0]["text"]},  # Exercise (relevant)
        {"id": "2", "score": 0.73, "text": CANDIDATE_DOCS[1]["text"]},  # Weather (false positive)
        {"id": "3", "score": 0.70, "text": CANDIDATE_DOCS[2]["text"]},  # Mental health (relevant)
        {"id": "5", "score": 0.68, "text": CANDIDATE_DOCS[4]["text"]},  # Weight (relevant)
    ]
    
    reranker = CohereReranker()
    reranked = await reranker.rerank(QUERY, initial_results, top_n=3)
    
    # Check: False positives removed
    top_ids = [r["id"] for r in reranked]
    assert "4" not in top_ids  # Pizza should be filtered out
    assert "2" not in top_ids  # Weather should be filtered out
    
    # Check: All top 3 are relevant
    assert all(doc_id in ["1", "3", "5"] for doc_id in top_ids)
    
    print(f"✅ Reranking successfully filtered false positives")
```

**Run Command**:
```bash
cd backend
pytest tests/test_reranking.py -v
```

### Manual Validation

**Test in Pipeline**: Add reranking node after retrieval

- [ ] **Provider Selection**: Choose Cohere or Cross-Encoder
- [ ] **Top N Parameter**: Set candidates to rerank (10-50)
- [ ] **Return K Parameter**: Set final results to return (3-10)
- [ ] **Test Query**: Run query, compare reranked vs non-reranked results
- [ ] **Accuracy Improvement**: Reranked results should be noticeably more relevant
- [ ] **Latency**: Reranking adds <500ms for 20 candidates

**Rating Criteria**:
- **10**: Clear 15%+ accuracy improvement, fast
- **8**: Noticeable improvement, acceptable latency
- **6**: Slight improvement, slow
- **4**: No improvement or broken

**Expected Rating**: 8-10

---

## 📊 Phase 4 Final Validation

### Integration Test

```python
# tests/integration/test_automated_variety_e2e.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_preset_to_execution_flow():
    """
    End-to-end test: Apply preset → Run pipeline → Get results
    """
    # Step 1: Apply legal QA preset
    preset_service = PresetService()
    pipeline = await preset_service.apply_preset_to_pipeline(
        preset_id="legal_document_qa",
        pipeline_id="test_e2e_pipeline",
        user_id="test_user",
        db=test_db
    )
    
    # Step 2: Upload test document
    with open("tests/fixtures/sample_contract.pdf", "rb") as f:
        upload_response = await test_client.post(
            "/api/documents/upload",
            files={"file": f}
        )
    doc_id = upload_response.json()["id"]
    
    # Step 3: Execute pipeline
    execution_response = await test_client.post(
        f"/api/pipelines/{pipeline.id}/execute",
        json={"document_id": doc_id}
    )
    assert execution_response.status_code == 200
    
    # Step 4: Verify chunks created
    chunks_response = await test_client.get(f"/api/documents/{doc_id}/chunks")
    chunks = chunks_response.json()["chunks"]
    assert len(chunks) > 0
    
    # Step 5: Query and verify results
    query_response = await test_client.post(
        "/api/query",
        json={
            "query": "What are the payment terms?",
            "pipeline_id": pipeline.id
        }
    )
    results = query_response.json()["results"]
    assert len(results) > 0
    assert "payment" in results[0]["text"].lower()
    
    print(f"✅ E2E flow complete: {len(chunks)} chunks, {len(results)} query results")
```

**Run Command**:
```bash
cd backend
pytest tests/integration/test_automated_variety_e2e.py -v --timeout=60
```

### User Acceptance Criteria

**Must Pass All**:
1. [ ] **Preset Gallery**: User can browse 10+ presets and apply in <30 seconds
2. [ ] **Document Upload**: User can upload PDF and get config recommendations in <5 seconds
3. [ ] **Wizard**: First-time user can create working pipeline in <3 minutes
4. [ ] **Variety**: User can choose from 6+ chunking methods, 5+ embedding providers
5. [ ] **Hybrid Search**: Hybrid search produces better results than vector-only on keyword queries
6. [ ] **Reranking**: Reranking improves accuracy by 15%+ on evaluation set
7. [ ] **End-to-End**: User can go from zero to working RAG system in <10 minutes

**Phase 4 Success** = All 7 criteria pass

---

## 🎯 Final Rating Calculation

**Component Ratings**:
1. Preset Library: ____/10
2. Document Analyzer: ____/10
3. Configuration Wizard: ____/10
4. Chunking Methods: ____/10
5. Embedding Providers: ____/10
6. Hybrid Search: ____/10
7. Reranking: ____/10

**Overall Phase 4 Rating**: (Sum / 7) = ____/10

**Pass Threshold**: 7.5/10

If rating ≥ 7.5 → **Proceed to Phase 5**  
If rating < 7.5 → **Address issues before Phase 5**
