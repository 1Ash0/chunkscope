import asyncio
import os
import json
import time

# Ensure backend acts as the source root
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.pipeline_executor import PipelineExecutor

async def test_parallelism_and_checkpointing():
    print("--- Testing Advanced Pipeline Engine ---")
    
    # Define a graph with parallel branches
    # A -> B, A -> C, (B, C) -> D
    nodes = [
        {"id": "A", "type": "loader", "config": {}},
        {"id": "B", "type": "llm", "config": {}},
        {"id": "C", "type": "llm", "config": {}},
        {"id": "D", "type": "evaluator", "config": {}},
    ]
    edges = [
        {"source": "A", "target": "B"},
        {"source": "A", "target": "C"},
        {"source": "B", "target": "D"},
        {"source": "C", "target": "D"},
    ]
    
    pipeline_id = "test_adv_001"
    executor = PipelineExecutor(nodes, edges, pipeline_id=pipeline_id)
    
    start_time = time.time()
    results = await executor.execute()
    duration = time.time() - start_time
    
    print(f"Execution Duration: {duration:.2f}s")
    # Each node takes 0.5s. 
    # Waves: {A} -> {B, C} -> {D}
    # Expected Time: 0.5 (A) + 0.5 (B&C parallel) + 0.5 (D) = 1.5s
    # If it was sequential, it would be 2.0s.
    
    if duration < 1.8:
        print("[PASS] Parallel execution confirmed (Duration < 1.8s)")
    else:
        print("[FAIL] Execution too slow, parallelism might be broken.")

    # Check for checkpoint
    checkpoint_path = f".pipelines/{pipeline_id}.json"
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r') as f:
            cp_data = json.load(f)
            if "A" in cp_data and "D" in cp_data:
                print("[PASS] Checkpoint saved and verified.")
            else:
                print("[FAIL] Checkpoint incomplete.")
    else:
        print("[FAIL] Checkpoint file not found.")

if __name__ == "__main__":
    asyncio.run(test_parallelism_and_checkpointing())
