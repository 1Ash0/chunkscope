import pytest
import asyncio
from app.services.rerankers.cohere_reranker import CohereReranker
from app.services.rerankers.cross_encoder_reranker import CrossEncoderReranker
from app.services.rerankers.rrf_reranker import ReciprocalRankFusionReranker

# Sample data for testing
SAMPLE_QUERY = "What are the rules for data privacy?"
SAMPLE_DOCS = [
    {"id": "doc1", "text": "Data privacy is protected by GDPR in Europe and various state laws in the US."},
    {"id": "doc2", "text": "The recipe for a perfect chocolate cake includes flour, sugar, and cocoa."},
    {"id": "doc3", "text": "CCPA provides California residents with specific rights regarding their personal data."},
    {"id": "doc4", "text": "The weather forecast for tomorrow shows clear skies and sunny intervals."},
    {"id": "doc5", "text": "Data protection officers are responsible for ensuring compliance with privacy regulations."},
]

@pytest.mark.asyncio
async def test_cohere_reranker():
    # Note: This requires a valid COHERE_API_KEY in .env
    try:
        reranker = CohereReranker()
        results = await reranker.rerank(SAMPLE_QUERY, SAMPLE_DOCS, top_k=3)
        
        assert len(results) <= 3
        # Check if the most relevant docs are at the top
        # doc1, doc3, doc5 are relevant to privacy
        relevant_ids = {"doc1", "doc3", "doc5"}
        assert results[0]["id"] in relevant_ids
        assert "rerank_score" in results[0]
    except ValueError:
        pytest.skip("Cohere API key not configured")
    except Exception as e:
        pytest.fail(f"Cohere reranking failed: {e}")

@pytest.mark.asyncio
async def test_cross_encoder_reranker():
    try:
        # Using the fastest model for testing
        reranker = CrossEncoderReranker(model_name="cross-encoder/ms-marco-TinyBERT-L-2-v2")
        results = await reranker.rerank(SAMPLE_QUERY, SAMPLE_DOCS, top_k=3)
        
        assert len(results) <= 3
        relevant_ids = {"doc1", "doc3", "doc5"}
        assert results[0]["id"] in relevant_ids
        assert "rerank_score" in results[0]
        # Verify sorting
        assert results[0]["rerank_score"] >= results[1]["rerank_score"]
    except ImportError:
        pytest.skip("sentence-transformers not installed")
    except Exception as e:
        pytest.fail(f"Cross-encoder reranking failed: {e}")

@pytest.mark.asyncio
async def test_rrf_reranker():
    reranker = ReciprocalRankFusionReranker(k=60)
    results = await reranker.rerank(SAMPLE_QUERY, SAMPLE_DOCS, top_k=3)
    
    assert len(results) == 3
    assert "rerank_score" in results[0]
    # RRF score for rank 0: 1 / (60 + 0 + 1) = 1/61
    assert results[0]["rerank_score"] == pytest.approx(1/61)
    # Verify order preservation (since single input)
    assert results[0]["id"] == "doc1"

@pytest.mark.asyncio
async def test_reranking_accuracy_improvement():
    # This is a conceptual test. In a real scenario, we'd compare 
    # metrics before and after reranking on a benchmark dataset.
    # Here we just verify that relevant docs move to the top.
    
    # Intentionally put relevant docs at the end
    shuffled_docs = [SAMPLE_DOCS[1], SAMPLE_DOCS[3], SAMPLE_DOCS[0]] # irrelevant, irrelevant, relevant
    
    reranker = CrossEncoderReranker(model_name="cross-encoder/ms-marco-TinyBERT-L-2-v2")
    results = await reranker.rerank(SAMPLE_QUERY, shuffled_docs, top_k=1)
    
    assert results[0]["id"] == "doc1" # Should be moved to top
