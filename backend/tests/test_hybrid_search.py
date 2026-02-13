import pytest
import numpy as np
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.retrievers.hybrid_retriever import HybridRetriever
from app.services.retrievers.mmr_retriever import MMRRetriever
from app.services.retrievers.parent_document_retriever import ParentDocumentRetriever
from app.models import Chunk

class MockRow:
    def __init__(self, chunk, score):
        self.Chunk = chunk
        self.score = score

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_chunks():
    chunks = []
    for i in range(10):
        c = MagicMock(spec=Chunk)
        c.id = uuid4()
        c.text = f"Chunk text {i}"
        c.embedding = [0.1] * 1536
        c.parent_chunk_id = None
        chunks.append(c)
    return chunks

@pytest.mark.asyncio
async def test_hybrid_search_combines_results(mock_db, mock_chunks):
    vector_results = [MockRow(mock_chunks[0], 0.75), MockRow(mock_chunks[1], 0.8)]
    keyword_results = [MockRow(mock_chunks[1], 0.95), MockRow(mock_chunks[2], 0.7)]
    
    res_vec = MagicMock()
    res_vec.all = MagicMock(return_value=vector_results)
    res_key = MagicMock()
    res_key.all = MagicMock(return_value=keyword_results)
    
    mock_db.execute = AsyncMock()
    mock_db.execute.side_effect = [res_vec, res_key]
    
    retriever = HybridRetriever(mock_db, alpha=0.5)
    results = await retriever.retrieve("test query", top_k=5, query_embedding=[0.1]*1536)
    
    assert len(results) >= 2
    assert results[0]["chunk"].id == mock_chunks[1].id

@pytest.mark.asyncio
async def test_alpha_parameter_effect(mock_db, mock_chunks):
    mock_db.execute = AsyncMock()
    
    # Pure vector (alpha=1.0)
    res_v = MagicMock()
    res_v.all = MagicMock(return_value=[MockRow(mock_chunks[0], 1.0)])
    
    mock_db.execute.side_effect = [res_v] # Only vector search called
    retriever_v = HybridRetriever(mock_db, alpha=1.0)
    res_v_out = await retriever_v.retrieve("test", query_embedding=[0.1]*1536)
    assert len(res_v_out) > 0
    assert res_v_out[0]["chunk"].id == mock_chunks[0].id
    
    # Pure keyword (alpha=0.0)
    res_k = MagicMock()
    res_k.all = MagicMock(return_value=[MockRow(mock_chunks[1], 1.0)])
    
    mock_db.execute.side_effect = [res_k] # Only keyword search called
    retriever_k = HybridRetriever(mock_db, alpha=0.0)
    res_k_out = await retriever_k.retrieve("test", query_embedding=[0.1]*1536)
    assert len(res_k_out) > 0
    assert res_k_out[0]["chunk"].id == mock_chunks[1].id

@pytest.mark.asyncio
async def test_mmr_reduces_redundancy(mock_db):
    c1 = MagicMock(spec=Chunk)
    c1.id = uuid4()
    c1.embedding = [1.0, 0.0, 0.0] + [0.0]*1533
    
    c2 = MagicMock(spec=Chunk)
    c2.id = uuid4()
    c2.embedding = [0.99, 0.01, 0.0] + [0.0]*1533
    
    c3 = MagicMock(spec=Chunk)
    c3.id = uuid4()
    c3.embedding = [0.0, 1.0, 0.0] + [0.0]*1533
    
    mock_results = [
        MockRow(c1, 1.0),
        MockRow(c2, 0.99),
        MockRow(c3, 0.5)
    ]
    
    mock_db.execute = AsyncMock(return_value=MagicMock(all=lambda: mock_results))
    
    retriever_rel = MMRRetriever(mock_db, lambda_mult=0.9)
    results_rel = await retriever_rel.retrieve("query", top_k=2, query_embedding=[1.0, 0.0, 0.0]+[0.0]*1533)
    ids_rel = [r["chunk"].id for r in results_rel]
    assert c1.id in ids_rel
    assert c2.id in ids_rel
    
    mock_db.execute = AsyncMock(return_value=MagicMock(all=lambda: mock_results))
    retriever_div = MMRRetriever(mock_db, lambda_mult=0.1)
    results_div = await retriever_div.retrieve("query", top_k=2, query_embedding=[1.0, 0.0, 0.0]+[0.0]*1533)
    ids_div = [r["chunk"].id for r in results_div]
    assert c1.id in ids_div
    assert c3.id in ids_div

@pytest.mark.asyncio
async def test_parent_document_retriever(mock_db):
    parent_id = uuid4()
    child = MagicMock(spec=Chunk)
    child.id = uuid4()
    child.parent_chunk_id = parent_id
    child.embedding = [0.1]*1536
    
    parent = MagicMock(spec=Chunk)
    parent.id = parent_id
    parent.text = "Parent context"
    
    res_child = MagicMock()
    res_child.all = MagicMock(return_value=[MockRow(child, 0.9)])
    
    res_parent = MagicMock()
    res_parent.scalars = MagicMock(return_value=MagicMock(all=lambda: [parent]))
    
    mock_db.execute = AsyncMock()
    mock_db.execute.side_effect = [res_child, res_parent]
    
    retriever = ParentDocumentRetriever(mock_db)
    results = await retriever.retrieve("query", query_embedding=[0.1]*1536)
    
    assert len(results) == 1
    assert results[0]["chunk"].id == parent_id
    assert results[0]["chunk"].text == "Parent context"
