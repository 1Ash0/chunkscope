import asyncio
import sys
import os
import importlib.util

# Load PipelineExecutor directly from file to avoid triggering app.services.__init__ dependencies
# (which fail due to missing aiofiles in the test environment)
file_path = os.path.join(os.path.dirname(__file__), 'app', 'services', 'pipeline_executor.py')
spec = importlib.util.spec_from_file_location("pipeline_executor", file_path)
module = importlib.util.module_from_spec(spec)
sys.modules["pipeline_executor"] = module
spec.loader.exec_module(module)

PipelineExecutor = module.PipelineExecutor
PipelineStatus = module.PipelineStatus

async def progress_callback(status: PipelineStatus):
    print(f"[{status.status}] Progress: {status.progress:.1f}% | Nodes: {status.current_nodes}")
    if status.error:
        print(f"ERROR: {status.error}")

async def main():
    print("--- Starting Pipeline Executor Test ---")
    
    # Diamond Graph: 
    #   Loader (A) -> Splitter (B)
    #   Loader (A) -> Cleaner (C)
    #   Splitter (B) -> Embedder (D)
    #   Cleaner (C) -> Embedder (D)
    
    nodes = [
        {"id": "A", "type": "LOADER"},
        {"id": "B", "type": "SPLITTER"},
        {"id": "C", "type": "CLEANER"},
        {"id": "D", "type": "EMBEDDER"}
    ]
    
    edges = [
        {"source": "A", "target": "B"},
        {"source": "A", "target": "C"},
        {"source": "B", "target": "D"},
        {"source": "C", "target": "D"}
    ]
    
    executor = PipelineExecutor(
        nodes=nodes, 
        edges=edges, 
        pipeline_id="test-run-1",
        progress_callback=progress_callback
    )
    
    print("Graph initialized. Executing...")
    try:
        results = await executor.execute()
        print("\n--- Execution Completed Successfully ---")
        print("Results:", results)
    except Exception as e:
        print(f"\n--- Execution Failed ---")
        print(e)
    
    # Test Cycle Detection
    print("\n--- Testing Cycle Detection ---")
    edges_cyclic = edges + [{"source": "D", "target": "A"}] # Cycle D->A
    executor_cyclic = PipelineExecutor(nodes, edges_cyclic)
    try:
        await executor_cyclic.execute()
    except ValueError as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
