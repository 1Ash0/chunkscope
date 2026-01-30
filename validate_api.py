import sys
import os
import json
import time
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

# Hack path
sys.path.insert(0, r"C:\Users\ASMIT\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages")
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db, get_current_user
from app.models import Document, User

# Mock DB and User
mock_db = AsyncMock()
mock_user = User(id=uuid4(), email="test@example.com")

async def override_get_db():
    yield mock_db

async def override_get_current_user():
    return mock_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def run_checks():
    checks = []
    score = 0
    
    # Setup Mock Data
    doc_id = uuid4()
    extracted_text = "AI is transforming industries. Machine learning advances rapidly. " * 50 # ~3000 chars
    
    # Mock DB Query returning document
    mock_result = MagicMock()
    mock_document = Document(
        id=doc_id, 
        user_id=mock_user.id, 
        extracted_text=extracted_text, 
        filename="test.pdf"
    )
    mock_result.scalar_one_or_none.return_value = mock_document
    mock_db.execute.return_value = mock_result

    print("Running API Validation Checks...")

    # Test 1: Valid Request
    start = time.time()
    payload = {
        "document_id": str(doc_id),
        "chunking_config": {
            "method": "sentence",
            "chunk_size": 100,
            "overlap": 10
        }
    }
    response = client.post("/api/v1/chunks/visualize", json=payload)
    duration = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        if len(data["chunks"]) > 0 and "bbox" in data["chunks"][0]:
            checks.append("[PASS] Test 1: Valid request returns chunks with bbox")
            score += 1
        else:
             checks.append(f"[FAIL] Test 1: Response missing chunks or bbox. Got: {data.keys()}")
    else:
        checks.append(f"[FAIL] Test 1: Status {response.status_code}. Body: {response.text}")

    # Test 2: Invalid ID (404)
    # Configure mock to return None for this specific call
    # We must reset the return_value to None explicitly
    mock_result_404 = MagicMock()
    mock_result_404.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result_404
    
    response_404 = client.post("/api/v1/chunks/visualize", json={
        "document_id": str(uuid4()),
        "chunking_config": {}
    })
    
    if response_404.status_code == 404:
        checks.append("[PASS] Test 2: Invalid ID returns 404")
        score += 1
    else:
        checks.append(f"[FAIL] Test 2: Expected 404, got {response_404.status_code}")

    # Test 3: Response Structure
    # Re-enable success mock for subsequent tests
    mock_db.execute.return_value = mock_result
    
    response = client.post("/api/v1/chunks/visualize", json=payload)
    data = response.json()
    
    required_keys = {"document_id", "chunks", "metrics"}
    if required_keys.issubset(data.keys()):
        metrics = data["metrics"]
        if "processing_time_ms" in metrics:
             checks.append("[PASS] Test 3: Response structure correct")
             score += 1
        else:
             checks.append("[FAIL] Test 3: Metrics missing processing_time_ms")
    else:
        checks.append(f"[FAIL] Test 3: Missing keys. Found {data.keys()}")

    # Test 4: Performance
    # We already measured Test 1
    print(f"Time taken: {duration:.4f}s")
    if duration < 5:
        checks.append("[PASS] Test 4: Performance < 5s")
        score += 1
    else:
        checks.append(f"[FAIL] Test 4: Too slow ({duration:.4f}s)")

    # Test 5: Error Messages
    # Test invalid config (overlap > chunk_size)
    mock_db.execute.return_value = mock_result
    bad_payload = {
        "document_id": str(doc_id),
        "chunking_config": {
            "chunk_size": 50,
            "overlap": 60
        }
    }
    response_err = client.post("/api/v1/chunks/visualize", json=bad_payload)
    if response_err.status_code == 400:
        err_data = response_err.json()
        # FastAPI/Starlette errors usually result in {"detail": "message"} or {"detail": [{"...": "..."}]}
        # But if we use app.core.errors.BadRequestError (which maps to HTTPException), it should be detail.
        # Let's check keys directly.
        if "detail" in err_data:
            checks.append("[PASS] Test 5: Error messages are clear")
            score += 1
        elif "error" in err_data:  # Custom error handler might return 'error'
             checks.append("[PASS] Test 5: Error messages are clear (found 'error')")
             score += 1
        else:
            checks.append(f"[FAIL] Test 5: Error body structure missing detail/error. Got: {err_data.keys()}")
    else:
        checks.append(f"[FAIL] Test 5: Expected 400 for bad config, got {response_err.status_code}")

    print("\nRESULTS:")
    for c in checks:
        print(c)

    rating = "FAIL"
    if score == 5:
        rating = "EXCELLENT"
    elif score >= 3:
        rating = "GOOD"
        
    print(f"\nRATING: {rating}")

if __name__ == "__main__":
    run_checks()
