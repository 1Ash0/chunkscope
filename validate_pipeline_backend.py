import asyncio
import sys
import os

# Hack path
sys.path.insert(0, r"C:\Users\ASMIT\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages")
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.services.pipeline_executor import PipelineExecutor

async def run_checks():
    print("Running Pipeline Backend Checks...")
    checks = []
    score = 0

    # Test 1: Linear Pipeline
    nodes = [
        {"id": "A", "type": "LOADER"},
        {"id": "B", "type": "CHUNKER"},
        {"id": "C", "type": "EMBEDDER"}
    ]
    edges = [
        {"source": "A", "target": "B"},
        {"source": "B", "target": "C"}
    ]
    
    print("Executing Test 1 (Linear)...")
    executor = PipelineExecutor(nodes, edges)
    results = await executor.execute()
    
    if len(results) == 3 and results["C"]["out"] == "Processed C":
        checks.append("[PASS] Test 1: Linear DAG execution passed")
        score += 1
    else:
        checks.append(f"[FAIL] Test 1: Unexpected results: {results}")

    # Test 2: Cycle Detection
    print("Executing Test 2 (Cycle)...")
    cycle_edges = edges + [{"source": "C", "target": "A"}]
    executor_cycle = PipelineExecutor(nodes, cycle_edges)
    try:
        await executor_cycle.execute()
        checks.append("[FAIL] Test 2: Cycle NOT detected")
    except ValueError as e:
        if "cycle" in str(e).lower():
            checks.append("[PASS] Test 2: Cycle detection passed")
            score += 1
        else:
            checks.append(f"[FAIL] Test 2: Unexpected error: {e}")

    # Test 3: Parallel Execution
    print("Executing Test 3 (Parallel)...")
    nodes_p = [
        {"id": "root", "type": "LOADER"},
        {"id": "p1", "type": "CHUNKER"},
        {"id": "p2", "type": "CHUNKER"},
        {"id": "join", "type": "EMBEDDER"}
    ]
    edges_p = [
        {"source": "root", "target": "p1"},
        {"source": "root", "target": "p2"},
        {"source": "p1", "target": "join"},
        {"source": "p2", "target": "join"}
    ]
    executor_p = PipelineExecutor(nodes_p, edges_p)
    results_p = await executor_p.execute()
    
    if len(results_p) == 4:
        checks.append("[PASS] Test 3: Parallel DAG execution passed")
        score += 1
    else:
        checks.append("[FAIL] Test 3: Parallel execution failed")

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
    asyncio.run(run_checks())
