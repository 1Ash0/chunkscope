import asyncio
import logging
from collections import defaultdict, deque
from typing import List, Dict, Any, Optional, Set, Callable
from pydantic import BaseModel
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# --- Data Models ---
class PipelineNode(BaseModel):
    id: str
    type: str
    config: Dict[str, Any] = {}

class PipelineEdge(BaseModel):
    source: str
    target: str

class PipelineStatus(BaseModel):
    pipeline_id: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    progress: float
    current_nodes: List[str]
    results: Dict[str, Any]
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# --- Executor Service ---
class PipelineExecutor:
    """
    Executes a DAG of nodes efficiently using asyncio.
    Supports parallelism, progress tracking, and cancellation.
    """
    def __init__(
        self, 
        nodes: List[Dict[str, Any]], 
        edges: List[Dict[str, Any]], 
        pipeline_id: str = "default",
        progress_callback: Optional[Callable[[PipelineStatus], None]] = None
    ):
        self.nodes = {n['id']: PipelineNode(**n) for n in nodes}
        self.edges = [PipelineEdge(**e) for e in edges]
        self.pipeline_id = pipeline_id
        self.callback = progress_callback
        
        self.adj = defaultdict(list)
        self.in_degree = defaultdict(int)
        self.results = {}
        self.status = PipelineStatus(
            pipeline_id=pipeline_id,
            status="PENDING",
            progress=0.0,
            current_nodes=[],
            results={}
        )
        self._build_graph()

    def _build_graph(self):
        """Constructs adjacency list and calculates in-degrees."""
        # Initialize in-degree for all nodes to 0
        for node_id in self.nodes:
            self.in_degree[node_id] = 0
            
        for edge in self.edges:
            self.adj[edge.source].append(edge.target)
            self.in_degree[edge.target] += 1

    def _detect_cycle(self) -> bool:
        """Kahn's algorithm check for cycles."""
        temp_in_degree = self.in_degree.copy()
        queue = deque([n for n in self.nodes if temp_in_degree[n] == 0])
        count = 0
        
        while queue:
            u = queue.popleft()
            count += 1
            for v in self.adj[u]:
                temp_in_degree[v] -= 1
                if temp_in_degree[v] == 0:
                    queue.append(v)
                    
        return count != len(self.nodes)

    async def execute(self):
        """Main execution method with wave-based parallelism and checkpointing."""
        if self._detect_cycle():
            raise ValueError("Pipeline contains a cycle (circular dependency).")

        self.status.status = "RUNNING"
        self.status.started_at = datetime.utcnow()
        self._emit_status()

        # Semaphores for resource-heavy nodes (API calls)
        api_semaphore = asyncio.Semaphore(5)
        
        # Initial set of ready nodes (in-degree 0)
        ready_queue = [n for n in self.nodes if self.in_degree[n] == 0]
        completed_count = 0
        total_nodes = len(self.nodes)

        try:
            while ready_queue:
                # 1. Update status
                self.status.current_nodes = ready_queue
                self._emit_status()

                # 2. Execute current wave in parallel
                logger.info(f"Executing wave: {ready_queue}")
                
                # We wrap each node execution with the semaphore if it's an API type
                async def sem_execute(node_id):
                    node = self.nodes[node_id]
                    if node.type in ["embedder", "llm", "reranker"]:
                        async with api_semaphore:
                            return await self._execute_node(node_id)
                    return await self._execute_node(node_id)

                tasks = [sem_execute(node_id) for node_id in ready_queue]
                wave_results = await asyncio.gather(*tasks, return_exceptions=True)

                # 3. Process results & Update next wave
                next_wave_candidates = []
                
                for node_id, result in zip(ready_queue, wave_results):
                    if isinstance(result, Exception):
                        logger.error(f"Node {node_id} failed: {result}")
                        # Optional: Mark node specifically in status
                        raise result 
                    
                    self.results[node_id] = result
                    completed_count += 1
                    
                    # Decrement neighbors
                    for neighbor in self.adj[node_id]:
                        self.in_degree[neighbor] -= 1
                        if self.in_degree[neighbor] == 0:
                            next_wave_candidates.append(neighbor)
                
                # 4. Checkpoint after each wave
                self._save_checkpoint()

                # 5. Prepare next wave
                ready_queue = next_wave_candidates
                progress_pct = (completed_count / total_nodes) * 100
                self.status.progress = progress_pct
                self._emit_status()

            self.status.status = "COMPLETED"
            self.status.completed_at = datetime.utcnow()
            self.status.results = self.results
            self._emit_status()
            
            return self.results

        except asyncio.CancelledError:
            self.status.status = "CANCELLED"
            self.status.error = "Pipeline execution was cancelled."
            self._emit_status()
            raise
        except Exception as e:
            self.status.status = "FAILED"
            self.status.error = str(e)
            self._emit_status()
            raise

    def _save_checkpoint(self):
        """Saves current results to disk for resumability."""
        import json
        import os
        checkpoint_dir = ".pipelines"
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_path = os.path.join(checkpoint_dir, f"{self.pipeline_id}.json")
        try:
            with open(checkpoint_path, 'w') as f:
                json.dump(self.results, f)
            logger.info(f"Checkpoint saved to {checkpoint_path}")
        except Exception as e:
            logger.warning(f"Failed to save checkpoint: {e}")

    async def _execute_node(self, node_id: str) -> Any:
        """
        Executes a specific node logic.
        Gathers inputs from all source nodes that point to this node.
        """
        node = self.nodes[node_id]
        logger.info(f"Starting node {node_id} ({node.type})")
        
        # 1. Gather inputs from parent nodes
        inputs = {}
        for edge in self.edges:
            if edge.target == node_id:
                # Get the result of the source node
                parent_result = self.results.get(edge.source)
                inputs[edge.source] = parent_result

        # 2. Extract specific data if needed? 
        # For now, we pass the raw dictionary of {parent_id: results}
        
        # 3. FAST PATH: Real Logic for Loader
        if node.type == "loader":
            # (Keeping existing loader logic...)
            # Check for path in config (from frontend) or assume inputs has it
            file_path = node.config.get("path")
            if not file_path:
                # Fallback to sample.pdf in frontend/public (relative to project root)
                base_dir = Path(__file__).resolve().parent.parent.parent.parent
                file_path = str(base_dir / "frontend" / "public" / "sample.pdf")
                logger.warning(f"No path provided for loader {node_id}, using default: {file_path}")
            
            # Sanitize: Remove surrounding quotes if user copied as path
            file_path = file_path.strip('"').strip("'")

            try:
                import fitz
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                
                return {
                    "node_type": "loader",
                    "file_path": file_path,
                    "text_preview": text[:200] + "...",
                    "full_text": text,
                    "full_text_length": len(text)
                }
            except Exception as e:
                logger.error(f"Failed to load PDF: {e}")
                raise e

        # 4. FAST PATH: Real Logic for LLM Generator
        if node.type == "llm":
            from app.config import settings
            # Secure Key Logic: Node Config > Env Var
            api_key = node.config.get("apiKey") or settings.openai_api_key
            
            if not api_key:
                logger.warning(f"No API Key provided for LLM node {node_id}. Using simulation.")
                await asyncio.sleep(0.5)
                return {
                    "node_type": "llm",
                    "response": "Simulation: No API Key provided (Set in Node or .env).",
                    "model": "simulated"
                }
            
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=api_key)
                
                # Construct Context
                context_str = ""
                for parent_id, result in inputs.items():
                    if isinstance(result, dict):
                        if "full_text" in result:
                            context_str += f"\nSOURCE ({parent_id}):\n{result['full_text'][:2000]}...\n"
                        elif "text_preview" in result:
                            context_str += f"\nSOURCE ({parent_id}):\n{result['text_preview']}\n"
                        elif "response" in result:
                            context_str += f"\nPREV OUTPUT ({parent_id}):\n{result['response']}\n"
                        elif "chunks" in result:
                             # Flatten chunks for context
                             text_chunks = [c['text'] for c in result['chunks'][:3]] # Take first 3
                             context_str += f"\nCHUNKS ({parent_id}):\n{' '.join(text_chunks)}...\n"

                if not context_str:
                    context_str = "No specific context provided."

                system_prompt = node.config.get("systemPrompt", "You are a helpful assistant.")
                user_prompt = f"Context: {context_str}\n\nTask: Summarize this or answer user query."

                response = await client.chat.completions.create(
                    model=node.config.get("model", "gpt-3.5-turbo"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=500
                )
                
                return {
                    "node_type": "llm",
                    "response": response.choices[0].message.content,
                    "model": response.model,
                    "usage": response.usage.total_tokens
                }
            except Exception as e:
                logger.error(f"OpenAI Call Failed: {e}")
                raise e

        # 5. FAST PATH: Real Logic for Splitter
        if node.type == "splitter":
            try:
                from app.services.chunking_service import chunking_service
                from app.schemas.chunk import ChunkingConfig
                
                # Gather text from parents
                raw_text = ""
                for parent_id, result in inputs.items():
                   if result and "full_text" in result:
                       raw_text += result["full_text"] + "\n\n"
                
                if not raw_text:
                    logger.warning("No text input for splitter.")
                    return {"node_type": "splitter", "chunks": [], "count": 0}

                # Config
                config = ChunkingConfig(
                    window_size=int(node.config.get("windowSize", 1)),
                    threshold=float(node.config.get("threshold", 0.5)),
                    min_chunk_size=int(node.config.get("minChunkSize", 100))
                )
                
                chunks = chunking_service.chunk(raw_text, config)
                
                return {
                    "node_type": "splitter",
                    "chunks": chunks,
                    "count": len(chunks)
                }
            except Exception as e:
                logger.error(f"Splitter Failed: {e}")
                raise e

        # 6. FAST PATH: Real Logic for Embedder
        if node.type == "embedder":
            try:
                from app.services.chunking_service import chunking_service
                
                # Gather chunks from parents
                all_chunks = []
                for parent_id, result in inputs.items():
                    if result and "chunks" in result:
                        all_chunks.extend(result["chunks"])
                
                if not all_chunks:
                     logger.warning("No chunks input for embedder.")
                     return {"node_type": "embedder", "embeddings_count": 0}

                # Extract text list
                texts = [c['text'] for c in all_chunks]
                
                # Use the model directly from service (already loaded)
                embeddings = chunking_service.model.encode(texts, convert_to_numpy=True)
                
                # We can't return numpy arrays jsonly
                embeddings_list = embeddings.tolist()
                
                return {
                    "node_type": "embedder",
                    "embeddings_count": len(embeddings_list),
                    "dim": len(embeddings_list[0]) if embeddings_list else 0,
                    # Don't return full embeddings to frontend, too heavy.
                    "preview": embeddings_list[0][:5] if embeddings_list else [] 
                }
            except Exception as e:
                logger.error(f"Embedder Failed: {e}")
                raise e

        # 7. Simulate others
        # In a production system, we would have a NodeHandler registry:
        # handler = self.registry.get(node.type)
        # return await handler.run(node.config, inputs)
        
        await asyncio.sleep(0.5) 
        
        return {
            "node_type": node.type,
            "processed_at": datetime.utcnow().isoformat(),
            "inputs_count": len(inputs)
        }

    def _emit_status(self):
        if self.callback:
            # fire and forget (or await if callback is async)
            try:
                if asyncio.iscoroutinefunction(self.callback):
                    asyncio.create_task(self.callback(self.status))
                else:
                    self.callback(self.status)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")

# --- Example Usage ---
# async def run_demo():
#     nodes = [
#         {"id": "A", "type": "LOADER"},
#         {"id": "B", "type": "CHUNKER"},
#         {"id": "C", "type": "EMBEDDER"}
#     ]
#     edges = [
#         {"source": "A", "target": "B"},
#         {"source": "B", "target": "C"}
#     ]
#     executor = PipelineExecutor(nodes, edges)
#     results = await executor.execute()
#     print(results)
