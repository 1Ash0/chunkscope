import pytest
import asyncio
from app.services.pipeline_executor import PipelineExecutor

@pytest.mark.asyncio
async def test_topological_sort():
    """
    Test that the executor correctly sorts nodes based on dependencies.
    """
    nodes = [
        {"id": "3", "type": "output", "config": {}},
        {"id": "1", "type": "input", "config": {}},
        {"id": "2", "type": "process", "config": {}},
    ]
    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
    ]
    
    executor = PipelineExecutor(nodes, edges)
    
    adj = executor.adj
    assert "1" in adj
    assert "2" in adj["1"]
    assert "3" in adj["2"]

@pytest.mark.asyncio
async def test_detect_cycle():
    """
    Test that the executor detects cycles in the graph.
    """
    nodes = [
        {"id": "1", "type": "A", "config": {}},
        {"id": "2", "type": "B", "config": {}},
    ]
    # 1 -> 2 -> 1 (Cycle)
    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "1"},
    ]
    
    executor = PipelineExecutor(nodes, edges)
    # Cycle detection happens in execute()
    with pytest.raises(ValueError, match="cycle"):
        await executor.execute()
