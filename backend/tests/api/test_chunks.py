"""
Chunk Endpoints Integration Tests
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from uuid import uuid4

from app.models import User, Document, Chunk, DocumentType


@pytest_asyncio.fixture
async def test_document_with_text(test_db, test_user: User) -> Document:
    """Create a test document with extracted text."""
    doc = Document(
        user_id=test_user.id,
        filename="test123.pdf",
        original_filename="test.pdf",
        file_path="./uploads/test123.pdf",
        file_type=DocumentType.PDF,
        file_size_bytes=1024,
        extracted_text="This is the first paragraph. It has multiple sentences. Here is another one.\n\nThis is a second paragraph. It also has sentences. The end.",
        is_processed=True,
    )
    test_db.add(doc)
    await test_db.commit()
    await test_db.refresh(doc)
    return doc


@pytest_asyncio.fixture
async def test_document_no_text(test_db, test_user: User) -> Document:
    """Create a test document without extracted text."""
    doc = Document(
        user_id=test_user.id,
        filename="unprocessed.pdf",
        original_filename="unprocessed.pdf",
        file_path="./uploads/unprocessed.pdf",
        file_type=DocumentType.PDF,
        file_size_bytes=512,
        extracted_text=None,
        is_processed=False,
    )
    test_db.add(doc)
    await test_db.commit()
    await test_db.refresh(doc)
    return doc


# ============================================
# Visualize Tests
# ============================================

@pytest.mark.asyncio
async def test_visualize_fixed_chunking(
    client: AsyncClient,
    auth_headers: dict,
    test_document_with_text: Document,
):
    """Test fixed-size chunking visualization."""
    response = await client.post(
        "/api/v1/chunks/visualize",
        headers=auth_headers,
        json={
            "document_id": str(test_document_with_text.id),
            "chunking_config": {
                "method": "fixed",
                "chunk_size": 50,
                "overlap": 10,
            },
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "chunks" in data
    assert "metrics" in data
    assert len(data["chunks"]) > 0
    assert data["metrics"]["total_chunks"] > 0


@pytest.mark.asyncio
async def test_visualize_sentence_chunking(
    client: AsyncClient,
    auth_headers: dict,
    test_document_with_text: Document,
):
    """Test sentence-based chunking visualization."""
    response = await client.post(
        "/api/v1/chunks/visualize",
        headers=auth_headers,
        json={
            "document_id": str(test_document_with_text.id),
            "chunking_config": {
                "method": "sentence",
                "chunk_size": 100,
                "overlap": 0,
            },
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["chunks"]) > 0


@pytest.mark.asyncio
async def test_visualize_paragraph_chunking(
    client: AsyncClient,
    auth_headers: dict,
    test_document_with_text: Document,
):
    """Test paragraph-based chunking visualization."""
    response = await client.post(
        "/api/v1/chunks/visualize",
        headers=auth_headers,
        json={
            "document_id": str(test_document_with_text.id),
            "chunking_config": {
                "method": "paragraph",
                "chunk_size": 500,
                "overlap": 0,
            },
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["chunks"]) >= 1


@pytest.mark.asyncio
async def test_visualize_recursive_chunking(
    client: AsyncClient,
    auth_headers: dict,
    test_document_with_text: Document,
):
    """Test recursive chunking visualization."""
    response = await client.post(
        "/api/v1/chunks/visualize",
        headers=auth_headers,
        json={
            "document_id": str(test_document_with_text.id),
            "chunking_config": {
                "method": "recursive",
                "chunk_size": 60,
                "overlap": 10,
            },
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["chunks"]) > 0


@pytest.mark.asyncio
async def test_visualize_document_not_processed(
    client: AsyncClient,
    auth_headers: dict,
    test_document_no_text: Document,
):
    """Test error when document has no extracted text."""
    response = await client.post(
        "/api/v1/chunks/visualize",
        headers=auth_headers,
        json={
            "document_id": str(test_document_no_text.id),
            "chunking_config": {"method": "fixed"},
        },
    )
    
    assert response.status_code == 400
    assert "not been processed" in response.json()["error"]


@pytest.mark.asyncio
async def test_visualize_invalid_overlap(
    client: AsyncClient,
    auth_headers: dict,
    test_document_with_text: Document,
):
    """Test error when overlap >= chunk_size."""
    response = await client.post(
        "/api/v1/chunks/visualize",
        headers=auth_headers,
        json={
            "document_id": str(test_document_with_text.id),
            "chunking_config": {
                "method": "fixed",
                "chunk_size": 50,
                "overlap": 60,  # Invalid: overlap > chunk_size
            },
        },
    )
    
    assert response.status_code == 400
    assert "Overlap must be less than" in response.json()["error"]


@pytest.mark.asyncio
async def test_visualize_document_not_found(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test 404 for non-existent document."""
    fake_id = uuid4()
    response = await client.post(
        "/api/v1/chunks/visualize",
        headers=auth_headers,
        json={
            "document_id": str(fake_id),
            "chunking_config": {"method": "fixed"},
        },
    )
    
    assert response.status_code == 404
