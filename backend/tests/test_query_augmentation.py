import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from app.services.query_augmentor import QueryAugmentor
from app.services.retrievers.multi_query_retriever import MultiQueryRetriever
from app.services.retrievers.hyde_retriever import HyDERetriever
from app.services.retrievers.query_expansion_retriever import QueryExpansionRetriever

@pytest.fixture
def mock_base_retriever():
    retriever = AsyncMock()
    # RRF needs 'id' or 'text' to key off
    retriever.retrieve = AsyncMock(return_value=[
        {"id": "doc1", "text": "result 1", "score": 0.9},
        {"id": "doc2", "text": "result 2", "score": 0.8}
    ])
    return retriever

@pytest.mark.asyncio
async def test_query_augmentor_multi_query():
    augmentor = QueryAugmentor(api_key="mock-key")
    with patch.object(augmentor, '_get_completion', new_callable=AsyncMock) as mocked_completion:
        mocked_completion.return_value = '["v1", "v2", "v3"]'
        variants = await augmentor.augment_multi_query("test query", num_variants=3)
        assert len(variants) == 3
        # Original query is usually added by the logic
        assert "test query" in variants

@pytest.mark.asyncio
async def test_hyde_retriever(mock_base_retriever):
    retriever = HyDERetriever(mock_base_retriever)
    with patch("app.services.query_augmentor.query_augmentor.augment_hyde", new_callable=AsyncMock) as mocked_hyde:
        mocked_hyde.return_value = "hypothetical answer"
        results = await retriever.retrieve("test query", top_k=5)
        assert len(results) == 2
        
        # Verify base retriever was called with hyde doc
        mock_base_retriever.retrieve.assert_called_once()
        
        # Check arguments safely (positional or keyword)
        call_args = mock_base_retriever.retrieve.call_args
        # args[0] is query if positional, or kwargs['query']
        actual_query = call_args.args[0] if call_args.args else call_args.kwargs.get("query")
        assert actual_query == "hypothetical answer"

@pytest.mark.asyncio
async def test_multi_query_retriever(mock_base_retriever):
    retriever = MultiQueryRetriever(mock_base_retriever, num_variants=2)
    with patch("app.services.query_augmentor.query_augmentor.augment_multi_query", new_callable=AsyncMock) as mocked_multi:
        mocked_multi.return_value = ["test query", "variant 1"]
        results = await retriever.retrieve("test query", top_k=5)
        
        # RRF logic should combine them, and since we have IDs, it should work
        assert len(results) > 0
        assert mock_base_retriever.retrieve.call_count == 2
