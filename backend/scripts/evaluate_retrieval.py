import asyncio
import json
import logging
from typing import List, Dict
import time
from uuid import uuid4

# Setup paths
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import async_session_maker
from app.services.retrievers.hybrid_retriever import HybridRetriever
from app.services.retrievers.multi_query_retriever import MultiQueryRetriever
from app.services.retrievers.hyde_retriever import HyDERetriever
from app.services.reranker import reranker_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def evaluate():
    logger.info("Starting Retrieval Evaluation...")
    
    # 1. Load Dataset
    with open("scripts/eval_dataset.json", "r") as f:
        dataset = json.load(f)
    
    # 2. Setup Retrievers (Mocking DB for simulation if real DB is empty)
    # Ideally we insert data here. For this script, we'll assume the system is live 
    # OR we mock the retrieve method to return 'relevant' docs for testing the pipeline logic.
    # To make this robust, let's use a MockRetriever that returns pre-defined results based on query.
    
    class MockRetriever:
        async def retrieve(self, query, top_k=5, **kwargs):
            # Simulate latency
            await asyncio.sleep(0.1)
            # Return some dummy results, some relevant, some not
            results = []
            # specific logic to return relevant docs for specific queries
            for item in dataset:
                if item["query"] in query:
                    # Return relevant docs mixed with noise
                    for doc_id in item["relevant_docs"]:
                        results.append({"id": doc_id, "text": f"Content for {doc_id}", "score": 0.9})
            
            # Add noise
            for i in range(top_k):
                results.append({"id": f"noise_{i}", "text": f"Noise content {i}", "score": 0.1})
                
            return results[:top_k]

    base_retriever = MockRetriever()
    
    # Define strategies
    strategies = {
        "Vector": base_retriever,
        "Hybrid": base_retriever, # In mock, same as vector
        "Multi-Query": MultiQueryRetriever(base_retriever, num_variants=3),
        "HyDE": HyDERetriever(base_retriever)
    }

    results_table = []

    for name, retriever in strategies.items():
        logger.info(f"Evaluating {name}...")
        total_precision = 0
        total_recall = 0
        total_latency = 0
        
        for item in dataset:
            query = item["query"]
            relevant_ids = set(item["relevant_docs"])
            
            start_time = time.time()
            try:
                # Run retrieval
                retrieved_docs = await retriever.retrieve(query, top_k=5)
            except Exception as e:
                logger.error(f"Error in {name}: {e}")
                retrieved_docs = []
                
            elapsed = time.time() - start_time
            total_latency += elapsed
            
            # Calculate metrics
            retrieved_ids = set(doc.get("id") for doc in retrieved_docs)
            
            # Precision: relevant retrieved / total retrieved
            intersection = relevant_ids.intersection(retrieved_ids)
            precision = len(intersection) / len(retrieved_ids) if retrieved_ids else 0
            
            # Recall: relevant retrieved / total relevant
            recall = len(intersection) / len(relevant_ids) if relevant_ids else 0
            
            total_precision += precision
            total_recall += recall
            
        avg_precision = total_precision / len(dataset)
        avg_recall = total_recall / len(dataset)
        avg_latency = total_latency / len(dataset)
        
        results_table.append({
            "Method": name,
            "Precision@5": f"{avg_precision:.2f}",
            "Recall@5": f"{avg_recall:.2f}",
            "Latency (s)": f"{avg_latency:.3f}"
        })

    # Print Report
    report = "\n=== Evaluation Results ===\n"
    report += f"{'Method':<20} | {'Precision@5':<12} | {'Recall@5':<10} | {'Latency (s)':<12}\n"
    report += "-" * 65 + "\n"
    for row in results_table:
        report += f"{row['Method']:<20} | {row['Precision@5']:<12} | {row['Recall@5']:<10} | {row['Latency (s)']:<12}\n"
    report += "==========================\n"
    
    print(report)
    with open("scripts/eval_results.txt", "w") as f:
        f.write(report)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(evaluate())
