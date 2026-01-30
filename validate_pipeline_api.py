import sys
import os
import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

# Hack path
sys.path.insert(0, r"C:\Users\ASMIT\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages")
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db, get_current_user
from app.models import User

# Mock DB and User (though pipeline route doesn't use DB yet, better safe)
mock_db = AsyncMock()
mock_user = User(id=uuid4(), email="pipeline-test@example.com")

async def override_get_db():
    yield mock_db

async def override_get_current_user():
    return mock_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def run_checks():
    print("Running Pipeline API Verification...")
    checks = []
    score = 0

    # Test 1: Valid Execution Request
    nodes = [
        {"id": "A", "type": "LOADER"},
        {"id": "B", "type": "CHUNKER"}
    ]
    edges = [
        {"source": "A", "target": "B"}
    ]
    
    response = client.post("/api/v1/pipeline/execute", json={
        "nodes": nodes,
        "edges": edges
    })
    
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "success" and "results" in data:
            checks.append("[PASS] Test 1: Pipeline API execution successful")
            score += 1
        else:
            checks.append(f"[FAIL] Test 1: Unexpected response: {data}")
    else:
        checks.append(f"[FAIL] Test 1: Status {response.status_code}. Body: {response.text}")

    # Test 2: Cycle Detection (Bad Request)
    cycle_edges = edges + [{"source": "B", "target": "A"}]
    response_cycle = client.post("/api/v1/pipeline/execute", json={
        "nodes": nodes,
        "edges": cycle_edges
    })
    
    if response_cycle.status_code == 400:
        checks.append("[PASS] Test 2: Cycle detected by API (400 Correct)")
        score += 1
    else:
        checks.append(f"[FAIL] Test 2: Expected 400 for cycle, got {response_cycle.status_code}")

    # Test 3: Large Graph Performance
    large_nodes = [{"id": f"n{i}", "type": "STEP"} for i in range(10)]
    large_edges = [{"source": f"n{i}", "target": f"n{i+1}"} for i in range(9)]
    
    import time
    start = time.time()
    response_large = client.post("/api/v1/pipeline/execute", json={
        "nodes": large_nodes,
        "edges": large_edges
    })
    duration = time.time() - start
    print(f"Large Pipeline Time: {duration:.2f}s")
    
    if response_large.status_code == 200:
        checks.append("[PASS] Test 3: Large pipeline executed successfully")
        score += 1
    else:
        checks.append(f"[FAIL] Test 3: Large pipeline failed")

    print("\nRESULTS:")
    for c in checks:
        print(c)

    rating = "FAIL"
    if score == 3:
        rating = "EXCELLENT"
    elif score >= 2:
        rating = "GOOD"
        
    print(f"\nRATING: {rating}")

if __name__ == "__main__":
    run_checks()
